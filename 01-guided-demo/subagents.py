"""
Sub-agent definitions — Guided Demo, Stage 2.

The SDK supports sub-agents via the built-in `Task` tool. The main agent
calls Task(subagent_type="researcher", prompt="...") and the SDK spins up a
fresh, isolated conversation with the named agent, runs it to completion,
and hands back the final answer.

Why bother? Two reasons that matter in production:

  1. **Context isolation.** The sub-agent's tool call chatter (search
     results, raw API responses, dead ends) stays in its own context
     window. Only the distilled answer flows back to the main agent.
     Your orchestrator's context stays clean.

  2. **Role specialization.** Each sub-agent gets its own system prompt,
     its own tool allowlist, even its own model. The fact-checker doesn't
     need the same instructions as the researcher.

Each AgentDefinition below becomes a valid subagent_type for the Task tool.
"""

from claude_agent_sdk import AgentDefinition

# ──────────────────────────────────────────────────────────────────────────────
# Tool names that sub-agents are allowed to use. These have to match the full
# mcp__<server>__<tool> names from tools.py. Sub-agents get their own
# allowlist — they can only touch what you give them here.
# ──────────────────────────────────────────────────────────────────────────────

_RESEARCH_TOOLS = [
    "mcp__research__search_company_news",
    "mcp__research__get_company_financials",
    "mcp__research__get_recent_press_releases",
    "mcp__research__get_competitive_landscape",
]


# ──────────────────────────────────────────────────────────────────────────────
# Sub-agent definitions
# ──────────────────────────────────────────────────────────────────────────────

SUBAGENTS: dict[str, AgentDefinition] = {
    # The researcher does the heavy lifting of information gathering. It has
    # access to all the research tools and is prompted to be exhaustive.
    # Using "haiku" keeps sub-agent spawns cheap and fast — the main agent
    # uses a bigger model for synthesis.
    "researcher": AgentDefinition(
        description=(
            "Gathers raw information about a company. Use for initial "
            "research before writing a briefing. Give it a specific "
            "research question, not a vague request."
        ),
        prompt=(
            "You are a thorough research analyst. When given a research "
            "question about a company, use every relevant tool to gather "
            "current information. Return structured findings with dates "
            "and sources. Don't editorialize — just report what you found."
        ),
        tools=_RESEARCH_TOOLS,
        model="haiku",
    ),
    # The fact-checker cross-references specific claims. It has the same
    # tools but a different mandate: verify, don't discover.
    "fact_checker": AgentDefinition(
        description=(
            "Verifies specific factual claims before they go into a "
            "briefing. Give it a claim and it will confirm, refute, or "
            "flag it as unverifiable using the available data sources."
        ),
        prompt=(
            "You are a fact-checker. You will be given one or more "
            "specific claims about a company. For each claim, use the "
            "research tools to confirm or refute it. Respond with one of: "
            "CONFIRMED (with source), REFUTED (with correction), or "
            "UNVERIFIABLE (if the data isn't available). Be strict — "
            "if a claim says 'Q4 revenue was $120M' and the actual number "
            "is $118M, that's REFUTED."
        ),
        tools=_RESEARCH_TOOLS,
        model="haiku",
    ),
}


# ──────────────────────────────────────────────────────────────────────────────
# When sub-agents are enabled, we append this to the main agent's system
# prompt so it knows to actually use them. Without this nudge, the model
# tends to just do everything itself.
# ──────────────────────────────────────────────────────────────────────────────

ORCHESTRATOR_PROMPT_SUFFIX = """

You have access to specialized sub-agents via the Task tool:

  • researcher — delegate information gathering. Use for the initial research
    phase. Give it a focused question like "Find Tinplate Merchant Systems' recent
    product announcements and Q4 financials."

  • fact_checker — delegate claim verification. Before finalizing your
    briefing, send your key factual claims to the fact-checker to confirm.

Prefer delegating over doing research yourself. Your job is synthesis and
judgment — let the sub-agents handle the legwork."""
