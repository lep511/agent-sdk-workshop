"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   CHIEF OF STAFF AGENT — CONFIG                                              ║
║                                                                              ║
║   This is your workspace. Pick components, write the prompt, iterate.        ║
║                                                                              ║
║   See ../COMPONENTS.md for the full menu of tool categories and sub-agents.  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pathlib import Path

AGENT_NAME = "Chief of Staff Agent"


# ──────────────────────────────────────────────────────────────────────────────
# COMPONENT SELECTION
#
# See ../COMPONENTS.md for the full menu of tool categories and sub-agents.
# Start with the defaults, run it, then add/remove/swap and see what changes.
# ──────────────────────────────────────────────────────────────────────────────

TOOL_CATEGORIES = [
    "schedule",     # calendar + email drafting — core for a CoS agent
    "knowledge",    # internal doc search
    "memory",       # remember the exec's preferences
]

SUBAGENTS = [
    "summarizer",   # condense long documents
    "writer",       # polish draft emails
]


# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
#
# This is where most of your iteration should happen. The components above
# give the agent *capabilities*; the prompt gives it *judgment*.
#
# Things to try:
#   - Add specific guardrails ("never draft emails to people outside the company")
#   - Shape the output format ("always structure briefings as: Context / Ask / Recommendation")
#   - Give it a persona ("you work for a CEO who hates jargon")
#   - Tell it how to use sub-agents ("delegate long-doc reading to the summarizer")
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a chief of staff for a busy executive. Your job is to \
protect their time, prepare them for meetings, and handle the first draft of \
anything routine.

Core behaviors:
- Before any meeting, check the calendar for context and search documents for \
relevant background
- When drafting emails, keep them short and direct — the exec will review \
before sending, so aim for 80% right rather than perfect
- Remember the exec's preferences (use save_memory) and apply them without \
being asked

When a request is ambiguous, make a reasonable assumption and state it \
clearly rather than asking clarifying questions. The exec values momentum \
over perfection."""


# The default task shown when you run the agent. Pressing Enter uses this;
# typing your own overrides it.
DEFAULT_TASK = (
    "I have a meeting with the board tomorrow about Q1 priorities. "
    "Check what's on my calendar tomorrow, pull any relevant prep docs, "
    "and give me a one-page briefing."
)


# ──────────────────────────────────────────────────────────────────────────────
# KNOBS — you probably won't change these, but they're here
# ──────────────────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-6"
VERBOSITY = "verbose"  # "verbose" shows tool calls; "normal" hides them
MAX_TURNS = 30         # safety cap on the agentic loop


# ══════════════════════════════════════════════════════════════════════════════
DATA_DIR = Path(__file__).parent / "data"
