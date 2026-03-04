"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   CUSTOMER SUPPORT AGENT — CONFIG                                            ║
║                                                                              ║
║   This is your workspace. Pick components, write the prompt, iterate.        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

See ../COMPONENTS.md for the full menu of tool categories and sub-agents.
"""

from pathlib import Path

AGENT_NAME = "Customer Support Agent"


# ──────────────────────────────────────────────────────────────────────────────
# COMPONENT SELECTION
# See ../COMPONENTS.md for the full menu.
# ──────────────────────────────────────────────────────────────────────────────

TOOL_CATEGORIES = [
    "support",      # lookup_customer, get_ticket, list_open_tickets, add_ticket_note
    "knowledge",    # search the help-center KB before answering
    "memory",       # remember customer-specific context across sessions
]

SUBAGENTS = [
    "classifier",   # triage tickets (billing? bug? feature request?)
    "writer",       # draft polished customer replies
]


# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
#
# The support agent's prompt needs to balance two failure modes:
#   - Too cautious → escalates everything, defeats the point
#   - Too confident → makes commitments it can't keep
#
# Where you draw that line is the interesting prompt-engineering challenge.
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a tier-1 customer support agent for a software company. \
Your job is to resolve tickets quickly and accurately, escalating only when \
genuinely necessary.

Workflow for each ticket:
1. Look up the customer — their plan tier and history affect what you can offer
2. Search the knowledge base — most questions have a documented answer
3. If it's a known issue with a documented fix, resolve it directly
4. If it requires account changes, refunds, or engineering work, add a note \
explaining your reasoning and escalate

Tone: warm but efficient. Customers want their problem solved, not a \
friendship. Acknowledge the frustration, then get to the fix.

Never promise timelines you can't control ("engineering will fix this by \
Friday"). Say what you can do and what happens next."""


DEFAULT_TASK = (
    "Triage ticket T-1047. Figure out what's going on, check if we have a "
    "documented fix, and either resolve it or escalate with a clear note."
)


# ──────────────────────────────────────────────────────────────────────────────
# KNOBS
# ──────────────────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-6"
VERBOSITY = "verbose"
MAX_TURNS = 30


# ══════════════════════════════════════════════════════════════════════════════
DATA_DIR = Path(__file__).parent / "data"
