"""
Glue layer: Claude Agent SDK running inside AWS Lambda Durable Functions.

Each SDK query() call (which internally runs the full agentic loop — model
invocations, tool executions, sub-agent dispatches) becomes a single durable
step. On replay, the entire result is returned from checkpoint without
re-running the agent.

For multi-phase workflows (plan → approve → execute), each phase is a
separate durable step — giving checkpoint boundaries between phases while
keeping full SDK features within each phase.

Usage:
    from aws_durable_execution_sdk_python import durable_execution, DurableContext
    from claude_agent_sdk import tool, create_sdk_mcp_server
    from lib.claude_durable import run_durable_agent

    @durable_execution
    def handler(event: dict, context: DurableContext) -> dict:
        return run_durable_agent(
            context,
            prompt=event["prompt"],
            system="You are a research assistant.",
            mcp_servers={"research": my_server},
            allowed_tools=["mcp__research__search_web"],
        )
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable

from aws_durable_execution_sdk_python import DurableContext
from aws_durable_execution_sdk_python.config import (
    Duration,
    WaitForCallbackConfig,
)

from claude_agent_sdk import ClaudeAgentOptions, AgentDefinition, query
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)


# ---------------------------------------------------------------------------
# Internal: async SDK bridge
# ---------------------------------------------------------------------------

async def _run_sdk_query_async(
    prompt: str,
    system: str,
    mcp_servers: dict | None,
    allowed_tools: list[str] | None,
    agents: dict[str, AgentDefinition] | None,
    model: str,
    max_turns: int,
) -> dict:
    """Drive claude_agent_sdk.query() to completion, return serializable result."""
    options = ClaudeAgentOptions(
        system_prompt=system,
        model=model,
        mcp_servers=mcp_servers or {},
        allowed_tools=allowed_tools or [],
        agents=agents or None,
        permission_mode="bypassPermissions",
        max_turns=max_turns,
    )

    messages_log: list[dict] = []

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    messages_log.append({"type": "text", "text": block.text})
                elif isinstance(block, ToolUseBlock):
                    messages_log.append({
                        "type": "tool_use",
                        "name": block.name,
                        "input": block.input,
                    })

        elif isinstance(message, ResultMessage):
            return {
                "response": message.result or "",
                "turns": message.num_turns,
                "total_cost_usd": message.total_cost_usd,
                "is_error": message.is_error,
                "session_id": message.session_id,
                "messages": messages_log,
            }

    return {
        "response": "Agent did not produce a result.",
        "turns": 0,
        "total_cost_usd": 0,
        "is_error": True,
        "session_id": None,
        "messages": messages_log,
    }


def _run_sdk_query_sync(
    prompt: str,
    system: str,
    mcp_servers: dict | None,
    allowed_tools: list[str] | None,
    agents: dict[str, AgentDefinition] | None,
    model: str,
    max_turns: int,
) -> dict:
    """Synchronous wrapper for the async SDK query — safe to call inside a durable step."""
    return asyncio.run(
        _run_sdk_query_async(
            prompt=prompt,
            system=system,
            mcp_servers=mcp_servers,
            allowed_tools=allowed_tools,
            agents=agents,
            model=model,
            max_turns=max_turns,
        )
    )


def _step_slug(prompt: str) -> str:
    """Create a short slug from the prompt for step naming."""
    words = prompt.split()[:4]
    slug = "-".join(w.lower().strip(".,!?") for w in words)
    return slug[:40]


# ---------------------------------------------------------------------------
# Public: run_durable_agent
# ---------------------------------------------------------------------------

def run_durable_agent(
    context: DurableContext,
    *,
    prompt: str,
    system: str = "You are a helpful assistant.",
    mcp_servers: dict | None = None,
    allowed_tools: list[str] | None = None,
    agents: dict[str, AgentDefinition] | None = None,
    model: str = "us.anthropic.claude-sonnet-4-6",
    max_turns: int = 10,
    step_name: str | None = None,
) -> dict:
    """Run a full Claude Agent SDK session as a single durable step.

    The SDK internally manages the agent loop (model → tool → model → ...),
    sub-agent dispatches, and MCP tool execution. The entire session result
    is checkpointed by the durable runtime.

    Args:
        context: The DurableContext from the Lambda handler.
        prompt: The user prompt to send to the agent.
        system: System prompt.
        mcp_servers: Dict of MCP server configs (from create_sdk_mcp_server).
        allowed_tools: Tool names the agent can use without permission prompts.
        agents: Sub-agent definitions (the orchestrator uses the Task tool).
        model: Bedrock model ID.
        max_turns: Maximum conversation turns for the agent.
        step_name: Override the durable step name (auto-generated if None).

    Returns:
        Dict with 'response', 'turns', 'total_cost_usd', 'is_error', etc.
    """
    name = step_name or f"sdk-agent-{_step_slug(prompt)}"

    # If agents are defined, ensure Task tool is in allowed_tools
    effective_tools = list(allowed_tools or [])
    if agents and "Task" not in effective_tools:
        effective_tools.append("Task")

    result = context.step(
        func=lambda step_ctx: _run_sdk_query_sync(
            prompt=prompt,
            system=system,
            mcp_servers=mcp_servers,
            allowed_tools=effective_tools,
            agents=agents,
            model=model,
            max_turns=max_turns,
        ),
        name=name,
    )
    return result


# ---------------------------------------------------------------------------
# Public: run_durable_agent_with_approval
# ---------------------------------------------------------------------------

def run_durable_agent_with_approval(
    context: DurableContext,
    *,
    prompt: str,
    system: str = "You are a helpful assistant.",
    mcp_servers: dict | None = None,
    allowed_tools: list[str] | None = None,
    agents: dict[str, AgentDefinition] | None = None,
    model: str = "us.anthropic.claude-sonnet-4-6",
    max_turns: int = 10,
    approval_timeout_hours: int = 24,
    notify_callback: Callable[[str, str], None] | None = None,
) -> dict:
    """Run a durable agent with human-in-the-loop approval.

    Flow:
      1. Agent generates a plan (SDK query, no tools) → checkpoint
      2. Function pauses via waitForCallback (zero compute cost)
      3. Human approves/rejects via AWS CLI or SDK
      4. If approved: agent executes plan with full tools → checkpoint
      5. If rejected: returns explanation

    Args:
        notify_callback: Called with (callback_id, plan_text) to send the
            approval request to a human (email, Slack, dashboard).
        approval_timeout_hours: How long to wait before timing out.
    """
    # Phase 1: Generate plan (no tools, just reasoning)
    plan_system = (
        f"{system}\n\n"
        "IMPORTANT: Do NOT execute any actions yet. Instead, produce a clear, "
        "numbered plan of what you intend to do. Start your response with "
        "'## Plan' and list the steps."
    )

    plan_result = context.step(
        func=lambda step_ctx: _run_sdk_query_sync(
            prompt=prompt,
            system=plan_system,
            mcp_servers=None,
            allowed_tools=[],
            agents=None,
            model=model,
            max_turns=1,
        ),
        name="generate-plan",
    )

    plan_text = plan_result["response"]
    context.logger.info("Plan generated, waiting for approval")

    # Phase 2: Wait for human approval (zero compute cost)
    def submit_approval(callback_id: str, ctx):
        if notify_callback:
            notify_callback(callback_id, plan_text)
        ctx.logger.info(
            "Approval request submitted",
            extra={"callback_id": callback_id},
        )

    approval = context.wait_for_callback(
        submitter=submit_approval,
        name="wait-for-human-approval",
        config=WaitForCallbackConfig(
            timeout=Duration.from_hours(approval_timeout_hours)
        ),
    )

    approval_data = json.loads(approval) if isinstance(approval, str) else approval
    approved = approval_data.get("approved", False)

    if not approved:
        reason = approval_data.get("reason", "No reason provided")
        return {
            "response": f"Plan was rejected. Reason: {reason}",
            "plan": plan_text,
            "approved": False,
            "turns": 1,
        }

    # Phase 3: Execute the approved plan (full SDK with tools)
    context.logger.info("Plan approved, executing")
    execute_prompt = (
        f"Your plan was approved. Execute it now.\n\n"
        f"Original request: {prompt}\n\n"
        f"Your plan:\n{plan_text}"
    )

    result = run_durable_agent(
        context,
        prompt=execute_prompt,
        system=system,
        mcp_servers=mcp_servers,
        allowed_tools=allowed_tools,
        agents=agents,
        model=model,
        max_turns=max_turns,
        step_name="execute-approved-plan",
    )
    result["plan"] = plan_text
    result["approved"] = True
    return result


# ---------------------------------------------------------------------------
# Public: run_multi_agent (convenience for fan-out pattern)
# ---------------------------------------------------------------------------

def run_multi_agent(
    context: DurableContext,
    *,
    sub_agents: dict[str, dict],
    synthesis_prompt: str,
    synthesis_system: str = "You are a senior analyst writing an executive briefing.",
    model: str = "us.anthropic.claude-sonnet-4-6",
) -> dict:
    """Run multiple specialized agents (each as a durable step), then synthesize.

    Each sub-agent is independently checkpointed. If Lambda crashes after
    2/3 agents complete, only the 3rd re-runs on replay.

    Args:
        sub_agents: Dict of agent_name -> config dict with keys:
            - prompt: str
            - system: str
            - mcp_servers: dict (optional)
            - allowed_tools: list[str] (optional)
            - max_turns: int (optional, default 3)
        synthesis_prompt: Prompt template with {agent_name} placeholders for results.
        synthesis_system: System prompt for the synthesis agent.
        model: Bedrock model ID.

    Returns:
        Dict with 'briefing' (synthesis), 'sub_agent_results', 'total_sub_agents'.
    """
    sub_results: dict[str, str] = {}

    for agent_name, config in sub_agents.items():
        result = run_durable_agent(
            context,
            prompt=config["prompt"],
            system=config["system"],
            mcp_servers=config.get("mcp_servers"),
            allowed_tools=config.get("allowed_tools"),
            model=model,
            max_turns=config.get("max_turns", 3),
            step_name=f"sub-agent-{agent_name}",
        )
        sub_results[agent_name] = result["response"]

        context.logger.info(
            f"Sub-agent completed: {agent_name}",
            extra={"turns": result["turns"]},
        )

    # Synthesis step
    formatted_prompt = synthesis_prompt.format(**sub_results)

    final = run_durable_agent(
        context,
        prompt=formatted_prompt,
        system=synthesis_system,
        mcp_servers=None,
        allowed_tools=[],
        model=model,
        max_turns=1,
        step_name="synthesize-results",
    )

    return {
        "briefing": final["response"],
        "sub_agent_results": sub_results,
        "total_sub_agents": len(sub_agents),
    }
