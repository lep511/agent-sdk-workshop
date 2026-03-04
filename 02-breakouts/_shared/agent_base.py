"""
The shared agent runner — every breakout uses this.

Each breakout's run.py is just:

    from _shared.agent_base import run
    import config
    run(config)

...and config.py is where attendees do the actual work: pick tool categories,
pick sub-agents, write the system prompt. This file translates those choices
into ClaudeAgentOptions and runs the loop.

You shouldn't need to edit this file during the workshop, but it's worth
reading. It's the same pattern as 01-guided-demo/agent.py:build_options(),
just generalized so any config shape works.
"""

import asyncio
import sys
from pathlib import Path
from types import ModuleType

from dotenv import load_dotenv

load_dotenv()

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import (
    AssistantMessage,
    UserMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)

from .tool_library import TOOL_CATALOG, set_data_dir, load_memory_context
from .subagent_library import SUBAGENT_CATALOG, SUBAGENT_REQUIRES


# ──────────────────────────────────────────────────────────────────────────────
# Console formatting
# ──────────────────────────────────────────────────────────────────────────────


class C:
    import os

    _on = os.environ.get("NO_COLOR") != "1"
    RESET = "\033[0m" if _on else ""
    BOLD = "\033[1m" if _on else ""
    DIM = "\033[2m" if _on else ""
    CYAN = "\033[96m" if _on else ""
    YELLOW = "\033[93m" if _on else ""
    GREEN = "\033[92m" if _on else ""
    RED = "\033[91m" if _on else ""
    MAGENTA = "\033[95m" if _on else ""
    GRAY = "\033[90m" if _on else ""


def _banner(text: str) -> None:
    print(f"\n{C.BOLD}{C.CYAN}{'═' * 70}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {text}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'═' * 70}{C.RESET}\n")


# ──────────────────────────────────────────────────────────────────────────────
# Config validation and options assembly
# ──────────────────────────────────────────────────────────────────────────────


def _validate(config: ModuleType) -> list[str]:
    """Check config for common mistakes and return warnings (non-fatal)."""
    warnings: list[str] = []

    for cat in getattr(config, "TOOL_CATEGORIES", []):
        if cat not in TOOL_CATALOG:
            warnings.append(
                f"Unknown tool category '{cat}'. "
                f"Available: {', '.join(TOOL_CATALOG.keys())}"
            )

    for agent in getattr(config, "SUBAGENTS", []):
        if agent not in SUBAGENT_CATALOG:
            warnings.append(
                f"Unknown sub-agent '{agent}'. "
                f"Available: {', '.join(SUBAGENT_CATALOG.keys())}"
            )
            continue
        # Check if required tool categories are enabled.
        for req in SUBAGENT_REQUIRES.get(agent, []):
            if req not in getattr(config, "TOOL_CATEGORIES", []):
                warnings.append(
                    f"Sub-agent '{agent}' works best with the '{req}' tool "
                    f"category enabled — consider adding it."
                )

    if not getattr(config, "SYSTEM_PROMPT", "").strip():
        warnings.append(
            "SYSTEM_PROMPT is empty. The agent will have no instructions."
        )

    return warnings


def _build_options(config: ModuleType) -> ClaudeAgentOptions:
    """Translate a config module into ClaudeAgentOptions.

    This is the Lego assembly step — taking the attendee's choices and
    wiring them into the SDK's option shape.
    """
    mcp_servers: dict = {}
    allowed_tools: list[str] = []
    agents: dict = {}

    # ── Tools ──────────────────────────────────────────────────────────────
    # Each enabled category contributes its MCP server and tool names.
    for cat in getattr(config, "TOOL_CATEGORIES", []):
        if cat in TOOL_CATALOG:
            server, tool_names = TOOL_CATALOG[cat]
            mcp_servers[cat] = server
            allowed_tools.extend(tool_names)

    # ── Sub-agents ─────────────────────────────────────────────────────────
    # Each enabled sub-agent adds an AgentDefinition. If any are enabled,
    # we also need the Task tool so the orchestrator can spawn them.
    for agent in getattr(config, "SUBAGENTS", []):
        if agent in SUBAGENT_CATALOG:
            agents[agent] = SUBAGENT_CATALOG[agent]
    if agents and "Task" not in allowed_tools:
        allowed_tools.append("Task")

    # ── System prompt ──────────────────────────────────────────────────────
    system_prompt = getattr(config, "SYSTEM_PROMPT", "").strip()

    # ── Memory (prompt-injection approach) ────────────────────────────────
    # This is SIMPLER than the hook approach from 01-guided-demo/memory.py.
    # There, a UserPromptSubmit hook fires on every turn and re-reads the
    # memory file — so mid-session saves are visible on the next turn.
    # Here, we inject once at startup via the system prompt — so mid-session
    # saves only appear on the NEXT run. Trades off freshness for simplicity.
    #
    # Why the simpler approach here? Breakout iteration is run → edit →
    # re-run. Startup-only injection is fine for that loop.
    #
    # STRETCH GOAL: Port the hook pattern from 01-guided-demo/memory.py into
    # this runner. You'd add a hooks= arg to ClaudeAgentOptions below and wire
    # in a HookMatcher. The guided demo's memory.py shows exactly how.
    if "memory" in getattr(config, "TOOL_CATEGORIES", []):
        mem = load_memory_context()
        if mem:
            system_prompt += f"\n\n{mem}"
        system_prompt += (
            "\n\nYou have access to persistent memory. When you learn "
            "something worth remembering for future sessions, call "
            "save_memory."
        )

    # If sub-agents are enabled, nudge the orchestrator to use them.
    if agents:
        agent_list = "\n".join(
            f"  • {name} — {defn.description}"
            for name, defn in agents.items()
        )
        system_prompt += (
            f"\n\nYou can delegate to these sub-agents via the Task tool:\n"
            f"{agent_list}\n\nPrefer delegation for specialized work."
        )

    return ClaudeAgentOptions(
        model=getattr(config, "MODEL", "claude-sonnet-4-6"),
        system_prompt=system_prompt or None,
        mcp_servers=mcp_servers,
        allowed_tools=allowed_tools,
        agents=agents or None,
        permission_mode="bypassPermissions",
        max_turns=getattr(config, "MAX_TURNS", None),
    )


def _print_config(config: ModuleType, warnings: list[str]) -> None:
    """Show the user exactly what's enabled."""
    tools = getattr(config, "TOOL_CATEGORIES", [])
    subagents = getattr(config, "SUBAGENTS", [])
    model = getattr(config, "MODEL", "claude-sonnet-4-6")

    print(f"{C.BOLD}Your agent configuration:{C.RESET}")
    print(f"  Model:       {model}")
    print(
        f"  Tools:       "
        f"{C.GREEN + ', '.join(tools) + C.RESET if tools else C.GRAY + 'none' + C.RESET}"
    )
    print(
        f"  Sub-agents:  "
        f"{C.GREEN + ', '.join(subagents) + C.RESET if subagents else C.GRAY + 'none' + C.RESET}"
    )
    prompt_len = len(getattr(config, "SYSTEM_PROMPT", ""))
    print(f"  Prompt:      {prompt_len} chars")
    print()

    for w in warnings:
        print(f"{C.YELLOW}  ⚠ {w}{C.RESET}")
    if warnings:
        print()


# ──────────────────────────────────────────────────────────────────────────────
# Message rendering — same as the guided demo
# ──────────────────────────────────────────────────────────────────────────────


def _render(message, verbose: bool) -> None:
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(f"{C.CYAN}{block.text}{C.RESET}")
            elif isinstance(block, ToolUseBlock) and verbose:
                inputs = ", ".join(
                    f"{k}={v!r}" for k, v in (block.input or {}).items()
                )
                print(
                    f"{C.DIM}{C.YELLOW}  → {block.name}({inputs}){C.RESET}"
                )

    elif isinstance(message, UserMessage) and verbose:
        for block in message.content:
            if isinstance(block, ToolResultBlock):
                text = str(block.content)
                if len(text) > 200:
                    text = text[:200] + "…"
                print(f"{C.DIM}  ← {text}{C.RESET}")

    elif isinstance(message, ResultMessage):
        print()
        if message.is_error:
            print(f"{C.RED}⚠ Error: {message.result}{C.RESET}")
        else:
            cost = message.total_cost_usd or 0.0
            print(
                f"{C.GRAY}[done — {message.num_turns} turn(s), "
                f"${cost:.4f}]{C.RESET}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# Main entry point — breakouts call run(config)
# ──────────────────────────────────────────────────────────────────────────────


async def _main(config: ModuleType) -> None:
    name = getattr(config, "AGENT_NAME", "Agent")
    data_dir = getattr(config, "DATA_DIR", None)
    verbose = getattr(config, "VERBOSITY", "verbose") == "verbose"

    _banner(name)

    # Point the tool library at this breakout's data.
    if data_dir:
        set_data_dir(Path(data_dir))

    warnings = _validate(config)
    _print_config(config, warnings)

    options = _build_options(config)

    # Prompt the user for a task.
    default = getattr(config, "DEFAULT_TASK", "How can I help?")
    print(f"{C.BOLD}What would you like to do?{C.RESET}")
    print(f"{C.GRAY}(press Enter for: {default!r}){C.RESET}")
    try:
        user_prompt = input("> ").strip()
    except EOFError:
        user_prompt = ""
    if not user_prompt:
        user_prompt = default
    print()

    # Multi-turn conversation loop — same pattern as the guided demo.
    async with ClaudeSDKClient(options=options) as client:
        await client.query(user_prompt)
        async for message in client.receive_response():
            _render(message, verbose)

        while True:
            print(f"\n{C.GRAY}(follow-up, or Enter to exit){C.RESET}")
            try:
                follow = input("> ").strip()
            except EOFError:
                break
            if not follow:
                break
            print()
            await client.query(follow)
            async for message in client.receive_response():
                _render(message, verbose)


def run(config: ModuleType) -> None:
    """Public entry point — breakout run.py files call this."""
    try:
        asyncio.run(_main(config))
    except KeyboardInterrupt:
        print(f"\n{C.GRAY}interrupted{C.RESET}")
        sys.exit(0)
