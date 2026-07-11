#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "claude-agent-sdk>=0.1.41",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""
Guided Demo — Company Research Briefing Agent

This is the single entry point for all four demo stages. You never need
to edit this file — just flip the toggles in config.py and re-run.

Run with:
    uv run agent.py

...or via the workshop script:
    ./workshop demo
"""

import asyncio
import sys

# Load ANTHROPIC_API_KEY from the repo-root .env file. load_dotenv() walks up
# the directory tree looking for a .env, so this works regardless of where
# you launch the script from.
from dotenv import load_dotenv

load_dotenv()

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher
from claude_agent_sdk.types import (
    AssistantMessage,
    UserMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
    HookEvent,
)

# Our own modules — all in this same directory.
import config
from tools import research_server, RESEARCH_TOOL_NAMES
from subagents import SUBAGENTS, ORCHESTRATOR_PROMPT_SUFFIX
from memory import load_memory_summary, make_memory_server, MEMORY_TOOL_NAMES, memory_hook


# Base system prompt for the briefing agent. The modules below add to this
# conditionally based on what's enabled.
BASE_SYSTEM_PROMPT = """You are a research assistant that prepares concise, \
well-sourced company briefings for a busy executive.

When asked to prepare a briefing on a company:
- Gather current information (use your tools if you have them)
- Lead with what matters most for a meeting: recent moves, financial \
position, things worth bringing up
- Be specific — cite dates, numbers, and sources when you have them
- Keep it tight — the executive has 90 seconds to read before walking in
- If you're working from memory alone (no tools), say so clearly

Never pad with generic boilerplate. If you don't know something, say so."""


# ──────────────────────────────────────────────────────────────────────────────
# Console formatting — small helpers to make the output readable
# ──────────────────────────────────────────────────────────────────────────────


class C:
    """ANSI color codes. Set NO_COLOR=1 in your env to disable."""

    import os

    _on = os.environ.get("NO_COLOR") != "1"
    RESET = "\033[0m" if _on else ""
    BOLD = "\033[1m" if _on else ""
    DIM = "\033[2m" if _on else ""
    CYAN = "\033[96m" if _on else ""
    YELLOW = "\033[93m" if _on else ""
    GREEN = "\033[92m" if _on else ""
    MAGENTA = "\033[95m" if _on else ""
    GRAY = "\033[90m" if _on else ""


def banner(text: str) -> None:
    print(f"\n{C.BOLD}{C.CYAN}{'─' * 70}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {text}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'─' * 70}{C.RESET}\n")


def _current_stage() -> tuple[int, str, str]:
    """Derive which stage the attendee is on from the three config flags.

    Returns (stage_number, stage_name, next_step_hint).
    """
    t, s, m = config.ENABLE_TOOLS, config.ENABLE_SUBAGENTS, config.ENABLE_MEMORY
    if not t and not s and not m:
        return (0, "Basic Chat", "flip ENABLE_TOOLS = True in config.py")
    if t and not s and not m:
        return (1, "Tools", "flip ENABLE_SUBAGENTS = True in config.py")
    if t and s and not m:
        return (2, "Sub-agents", "flip ENABLE_MEMORY = True in config.py")
    if t and s and m:
        return (3, "Memory & Context", "done — head to 02-breakouts/")
    # Off-path configs (e.g., memory on but tools off) — just report it.
    return (-1, "Custom", "see GUIDE.md for the standard progression")


def print_config() -> None:
    """Show the user which capabilities are enabled and where they are
    in the four-stage progression."""

    def flag(enabled: bool) -> str:
        return f"{C.GREEN}ON {C.RESET}" if enabled else f"{C.GRAY}off{C.RESET}"

    print(f"{C.BOLD}Current config (edit config.py to change):{C.RESET}")
    print(f"  ENABLE_TOOLS     = {flag(config.ENABLE_TOOLS)}")
    print(f"  ENABLE_SUBAGENTS = {flag(config.ENABLE_SUBAGENTS)}")
    print(f"  ENABLE_MEMORY    = {flag(config.ENABLE_MEMORY)}")
    print(f"  MODEL            = {config.MODEL}")
    print()

    stage_num, stage_name, next_hint = _current_stage()
    if stage_num >= 0:
        print(f"  {C.BOLD}{C.MAGENTA}→ Stage {stage_num} of 3: {stage_name}{C.RESET}")
    else:
        print(f"  {C.BOLD}{C.MAGENTA}→ {stage_name} config{C.RESET}")
    print(f"  {C.GRAY}Next: {next_hint}{C.RESET}")
    print(f"  {C.GRAY}Guide: 01-guided-demo/GUIDE.md{C.RESET}")
    print()


def show_assembled_prompt(options: ClaudeAgentOptions) -> None:
    """Dump everything the SDK is about to send to the model.

    Invoked via --show-prompt. This is the "peek under the hood" view:
    the full system context, every allowed tool, every sub-agent definition.
    Normally this is invisible — the SDK assembles it and sends it. Seeing
    it once is useful for understanding what "enabling a capability" actually
    means in terms of what the model receives.
    """
    banner("Assembled Context (--show-prompt)")

    print(f"{C.BOLD}SYSTEM PROMPT:{C.RESET}")
    print(f"{C.DIM}{options.system_prompt}{C.RESET}")
    print()

    tools = options.allowed_tools or []
    print(f"{C.BOLD}ALLOWED TOOLS ({len(tools)}):{C.RESET}")
    if tools:
        for t in tools:
            print(f"  {C.YELLOW}{t}{C.RESET}")
    else:
        print(f"  {C.GRAY}(none — no tools enabled){C.RESET}")
    print()

    agents = options.agents or {}
    print(f"{C.BOLD}SUB-AGENTS ({len(agents)}):{C.RESET}")
    if agents:
        for name, defn in agents.items():
            print(f"  {C.MAGENTA}{name}{C.RESET}")
            print(f"    {C.DIM}description:{C.RESET} {defn.description}")
            print(f"    {C.DIM}model:{C.RESET} {defn.model or '(inherits)'}")
            print(f"    {C.DIM}tools:{C.RESET} {len(defn.tools or [])} allowed")
            print(f"    {C.DIM}prompt:{C.RESET} {(defn.prompt or '')[:80]}...")
    else:
        print(f"  {C.GRAY}(none — no sub-agents enabled){C.RESET}")
    print()

    hooks = options.hooks or {}
    print(f"{C.BOLD}HOOKS:{C.RESET}")
    if hooks:
        for event, matchers in hooks.items():
            print(f"  {C.CYAN}{event}{C.RESET} — {len(matchers)} handler(s)")
        print(f"  {C.GRAY}Note: hook-injected context (like memory) is added at")
        print(f"  runtime per-turn, not shown here. See memory.py.{C.RESET}")
    else:
        print(f"  {C.GRAY}(none){C.RESET}")
    print()

    print(f"{C.BOLD}OTHER:{C.RESET}")
    print(f"  model:           {options.model}")
    print(f"  permission_mode: {options.permission_mode}")
    # mcp_servers can be a dict, a config file path, or None. In this demo
    # it's always a dict (we build it in-process), so just handle that case.
    servers = options.mcp_servers
    server_names = list(servers.keys()) if isinstance(servers, dict) else []
    print(f"  mcp_servers:     {server_names or '(none)'}")
    print()
    print(f"{C.GRAY}{'─' * 70}{C.RESET}")
    print(f"{C.GRAY}This is what the SDK assembled from your config. Every toggle")
    print(f"in config.py maps to one of the fields above. That's the lesson.{C.RESET}")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# The interesting part: building ClaudeAgentOptions from config toggles
#
# This function is the core of the guided demo lesson. Each block below
# corresponds to one of the toggles in config.py, and shows exactly which
# SDK option gets set when that capability is enabled.
# ──────────────────────────────────────────────────────────────────────────────


def build_options() -> ClaudeAgentOptions:
    """Assemble agent options based on the toggles in config.py.

    This is where each "stage" gets wired in. Reading this function
    top-to-bottom shows you the progression:

      Stage 0 → just a system prompt and a model
      Stage 1 → + mcp_servers + allowed_tools
      Stage 2 → + agents (and the Task tool to spawn them)
      Stage 3 → + a memory tool + a hook that injects remembered context
    """

    # Start with the pieces that are always present.
    system_prompt = BASE_SYSTEM_PROMPT
    allowed_tools: list[str] = []
    mcp_servers: dict = {}
    agents = None
    # HookEvent is a Literal type — annotating here so pyright accepts the
    # dict we build below. At runtime it's just a string key.
    hooks: dict[HookEvent, list[HookMatcher]] | None = None

    # ── Stage 1: TOOLS ──────────────────────────────────────────────────────
    # Wiring in custom tools takes two steps:
    #   1. Register the MCP server (bundle of tools) under a key
    #   2. List each tool's full name in allowed_tools
    # Without step 2, the model can see the tools exist but can't call them.
    if config.ENABLE_TOOLS:
        mcp_servers["research"] = research_server
        allowed_tools.extend(RESEARCH_TOOL_NAMES)

    # ── Stage 2: SUB-AGENTS ─────────────────────────────────────────────────
    # The SDK's sub-agent model: you define named AgentDefinitions (each with
    # its own system prompt, tool allowlist, and optional model override) and
    # the main agent delegates to them via the built-in "Task" tool.
    #
    # The main agent calls Task(subagent_type="researcher", prompt="...") and
    # the SDK spins up an isolated sub-agent conversation, runs it to
    # completion, and returns the result — all without polluting the main
    # context window.
    if config.ENABLE_SUBAGENTS:
        if not config.ENABLE_TOOLS:
            # Not a hard requirement of the SDK, but our sub-agents are
            # pointless without the research tools.
            print(
                f"{C.YELLOW}Note: ENABLE_SUBAGENTS works best with "
                f"ENABLE_TOOLS = True{C.RESET}\n"
            )
        agents = SUBAGENTS
        allowed_tools.append("Task")
        # Nudge the orchestrator to actually delegate instead of doing
        # everything itself.
        system_prompt += ORCHESTRATOR_PROMPT_SUFFIX

    # ── Stage 3: MEMORY ─────────────────────────────────────────────────────
    # Two parts:
    #   1. A save_memory tool so the agent can explicitly record things
    #      ("The user prefers bullet points")
    #   2. A UserPromptSubmit hook that reads the memory file at the start of
    #      each turn and injects what it finds as additional context
    #
    # The file persists between runs, so tomorrow's session picks up where
    # today left off.
    if config.ENABLE_MEMORY:
        mcp_servers["memory"] = make_memory_server()
        allowed_tools.extend(MEMORY_TOOL_NAMES)
        hooks = {"UserPromptSubmit": [memory_hook]}
        system_prompt += (
            "\n\nYou have a persistent memory. When the user expresses a "
            "preference or you produce a briefing that might be referenced "
            "later, use the save_memory tool to record it. Your past "
            "memories are automatically provided at the start of each "
            "conversation."
        )

    return ClaudeAgentOptions(
        model=config.MODEL,
        system_prompt=system_prompt,
        mcp_servers=mcp_servers,
        allowed_tools=allowed_tools,
        agents=agents,
        hooks=hooks,
        # bypassPermissions lets the agent use its allowed tools without
        # prompting the user for approval each time. In production you'd
        # likely use "default" and a can_use_tool callback — but for the
        # workshop we want smooth demos.
        permission_mode="bypassPermissions",
    )


# ──────────────────────────────────────────────────────────────────────────────
# Output handling — renders the SDK message stream
# ──────────────────────────────────────────────────────────────────────────────


def render_message(message, verbose: bool) -> None:
    """Print a single message from the SDK stream.

    The SDK yields several message types as the agent runs. In "normal"
    verbosity we only show the assistant's text. In "verbose" we also
    show tool calls and sub-agent activity — useful for seeing what
    changed between stages.
    """

    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                # The actual assistant reply — always show this.
                print(f"{C.CYAN}{block.text}{C.RESET}")
            elif isinstance(block, ToolUseBlock) and verbose:
                # The model decided to call a tool.
                inputs = ", ".join(
                    f"{k}={v!r}" for k, v in (block.input or {}).items()
                )
                print(
                    f"{C.DIM}{C.YELLOW}  → calling {block.name}"
                    f"({inputs}){C.RESET}"
                )

    elif isinstance(message, UserMessage) and verbose:
        # Tool results come back as UserMessages containing ToolResultBlocks.
        # The SDK automatically feeds these back to the model — we just
        # display them so attendees can see the round-trip.
        for block in message.content:
            if isinstance(block, ToolResultBlock):
                # Truncate long results to keep the console readable.
                text = str(block.content)
                if len(text) > 200:
                    text = text[:200] + "…"
                print(f"{C.DIM}  ← tool returned: {text}{C.RESET}")

    elif isinstance(message, ResultMessage):
        # Final summary emitted once the agent turn is complete.
        print()
        if message.is_error:
            print(f"{C.YELLOW}⚠ Finished with error: {message.result}{C.RESET}")
        else:
            cost = message.total_cost_usd or 0.0
            print(
                f"{C.GRAY}[done — {message.num_turns} turn(s), "
                f"${cost:.4f}]{C.RESET}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# Main loop
# ──────────────────────────────────────────────────────────────────────────────


async def main() -> None:
    banner("Company Research Briefing Agent")
    print_config()

    if config.ENABLE_MEMORY:
        summary = load_memory_summary()
        if summary:
            print(f"{C.MAGENTA}Loaded memories from previous sessions:{C.RESET}")
            print(f"{C.DIM}{summary}{C.RESET}\n")

    # Ask the user what they want. Pressing Enter uses the default from
    # config.py — keeps the 8-minute exercises moving.
    print(f"{C.BOLD}What would you like a briefing on?{C.RESET}")
    print(f"{C.GRAY}(press Enter for default: {config.DEFAULT_TASK!r}){C.RESET}")
    try:
        user_prompt = input("> ").strip()
    except EOFError:
        user_prompt = ""
    if not user_prompt:
        user_prompt = config.DEFAULT_TASK
    print()

    options = build_options()

    # --show-prompt: dump the assembled context and exit. Useful for seeing
    # exactly what the SDK is sending to the model at each stage.
    if "--show-prompt" in sys.argv:
        show_assembled_prompt(options)
        return

    verbose = config.VERBOSITY == "verbose"

    # ClaudeSDKClient (vs the simpler query() function) gives us a persistent
    # connection — useful for multi-turn follow-ups, and required for hooks
    # to fire reliably. The async-with block handles connection lifecycle.
    async with ClaudeSDKClient(options=options) as client:
        await client.query(user_prompt)

        # receive_response() yields messages until the agent's turn is done
        # (terminates after ResultMessage). The SDK is running the full
        # agentic loop internally — tool execution, result feeding, retry
        # handling. We're just subscribing to the event stream.
        async for message in client.receive_response():
            render_message(message, verbose)

        # Follow-up loop: keep the same client alive so the conversation
        # context carries forward. This is "within-session" memory — it
        # works even with ENABLE_MEMORY=False, but only until you exit.
        while True:
            print(f"\n{C.GRAY}(follow-up question, or press Enter to exit){C.RESET}")
            try:
                follow = input("> ").strip()
            except EOFError:
                break
            if not follow:
                break
            print()
            await client.query(follow)
            async for message in client.receive_response():
                render_message(message, verbose)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{C.GRAY}interrupted{C.RESET}")
        sys.exit(0)
