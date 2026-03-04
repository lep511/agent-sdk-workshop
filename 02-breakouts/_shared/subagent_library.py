"""
The sub-agent library — pre-built AgentDefinitions any breakout can enable.

Same AgentDefinition pattern you saw in the guided demo. Each sub-agent has
focused role, its own system prompt, and its own tool allowlist.

─── A note on tool access ────────────────────────────────────────────────────

Each sub-agent below declares which tool *categories* it needs (via the
_tools_for() helper). Those categories also have to be enabled in your
breakout's config — a sub-agent can only use a tool if the main agent has
that tool's MCP server registered.

If you enable a sub-agent without enabling its tool categories, it'll
still run but will just… think really hard without any data. The agent_base
runner prints a warning when it detects this misconfiguration.
"""

from claude_agent_sdk import AgentDefinition

from .tool_library import TOOL_CATALOG


def _tools_for(*categories: str) -> list[str]:
    """Flatten the tool names for one or more categories into a single
    allowlist. Missing categories are silently skipped — agent_base.py
    handles warning the user."""
    names: list[str] = []
    for cat in categories:
        if cat in TOOL_CATALOG:
            names.extend(TOOL_CATALOG[cat][1])
    return names


# ══════════════════════════════════════════════════════════════════════════════
# The catalog
# ══════════════════════════════════════════════════════════════════════════════

SUBAGENT_CATALOG: dict[str, AgentDefinition] = {
    # General-purpose research gatherer. Give it a focused question, it
    # digs through whatever data sources are available and returns a
    # structured summary.
    "researcher": AgentDefinition(
        description=(
            "Gathers information on a focused research question. Use for "
            "initial data collection before synthesis. Give it a specific "
            "question, not a vague topic."
        ),
        prompt=(
            "You are a research analyst. Given a specific question, use "
            "every relevant tool to gather information. Return structured "
            "findings with sources. Don't editorialize — report what you "
            "found and flag gaps."
        ),
        tools=_tools_for("knowledge", "support", "ops", "schedule"),
        model="haiku",
    ),

    # Condenses long content. Useful when the main agent has a lot of raw
    # data (long documents, many tickets) and needs a digest.
    "summarizer": AgentDefinition(
        description=(
            "Summarizes long content into key points. Use when you have "
            "a lot of raw material (documents, ticket threads, metrics) "
            "and need a digest."
        ),
        prompt=(
            "You are a summarization specialist. You will receive a body "
            "of text or data. Produce a concise summary (under 150 words) "
            "that captures the essential points. Preserve specific numbers, "
            "dates, and names — don't abstract them away."
        ),
        tools=[],  # summarizer works from the prompt it's given, no tools needed
        model="haiku",
    ),

    # Categorizes/routes content. Good for the customer-support breakout
    # (what kind of ticket is this?) and SRE (what class of incident?).
    "classifier": AgentDefinition(
        description=(
            "Classifies an item into a category. Use for routing tickets "
            "('billing' vs 'technical'), triaging incidents ('capacity' vs "
            "'code regression'), or tagging content."
        ),
        prompt=(
            "You are a classification specialist. You will receive an item "
            "and a set of possible categories. Respond with exactly one "
            "category and a one-sentence justification. If none fit well, "
            "say so explicitly rather than forcing a bad fit."
        ),
        tools=[],
        model="haiku",
    ),

    # Verifies specific claims against data sources. Same role as the
    # fact_checker in the guided demo — catches hallucination before it ships.
    "verifier": AgentDefinition(
        description=(
            "Verifies specific factual claims against available data. "
            "Use before finalizing any answer that cites numbers, dates, "
            "or customer details."
        ),
        prompt=(
            "You are a fact-checker. You will receive one or more claims. "
            "For each, use the available tools to verify. Respond with "
            "CONFIRMED (with source), REFUTED (with correction), or "
            "UNVERIFIABLE. Be strict — a small discrepancy is still REFUTED."
        ),
        tools=_tools_for("knowledge", "support", "ops"),
        model="haiku",
    ),

    # Takes rough notes and produces polished prose. Useful for
    # chief-of-staff (turn bullets into an email) and customer support
    # (draft a clear customer reply).
    "writer": AgentDefinition(
        description=(
            "Drafts polished prose from rough notes or bullet points. "
            "Use when you have the content but need it formatted for "
            "human consumption — emails, customer replies, summaries."
        ),
        prompt=(
            "You are a professional writer. You will receive notes, bullet "
            "points, or rough content along with instructions about tone "
            "and audience. Produce clean, well-organized prose. Match the "
            "requested tone exactly — formal for executives, warm for "
            "customers, precise for engineers."
        ),
        tools=[],
        model="haiku",
    ),

    # Walks through procedural steps. Useful for SRE (runbook execution)
    # and any agent that needs to follow a documented process.
    "procedure_runner": AgentDefinition(
        description=(
            "Walks through a documented procedure step by step, reporting "
            "on each step. Use for runbook execution or any task with a "
            "defined checklist."
        ),
        prompt=(
            "You are a procedure execution specialist. You will receive a "
            "set of steps. Work through them in order using your tools. "
            "For each step, report what you did and what you observed. "
            "If a step fails or you can't complete it, stop and report the "
            "blocker — don't skip ahead."
        ),
        tools=_tools_for("ops", "support"),
        model="haiku",
    ),
}


# Tool categories each sub-agent depends on. Used by agent_base.py to warn
# when you enable a sub-agent without its required tool categories.
SUBAGENT_REQUIRES: dict[str, list[str]] = {
    "researcher": ["knowledge"],  # at minimum, though it can use more
    "summarizer": [],
    "classifier": [],
    "verifier": ["knowledge"],
    "writer": [],
    "procedure_runner": ["ops"],
}
