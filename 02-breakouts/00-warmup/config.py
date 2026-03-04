"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   WARMUP — THE BRIDGE FROM GUIDED DEMO TO BREAKOUTS                          ║
║                                                                              ║
║   Same company-briefing task you just did in 01-guided-demo/, but now        ║
║   you're assembling the agent the breakout way: pick tool categories,        ║
║   pick sub-agents, write the prompt. No booleans.                            ║
║                                                                              ║
║   See ../COMPONENTS.md for the full menu.                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pathlib import Path

AGENT_NAME = "Company Briefing Agent (Warmup)"


# ──────────────────────────────────────────────────────────────────────────────
# COMPONENT SELECTION
#
# In the guided demo you flipped ENABLE_TOOLS / ENABLE_SUBAGENTS / ENABLE_MEMORY.
# Here you pick from categories instead. Same capabilities, different interface.
#
# The starting config below is roughly equivalent to "all three flags on" from
# the guided demo. Try removing "memory" or the sub-agents and re-running —
# you should recognize the behavior from stages 1/2/3.
# ──────────────────────────────────────────────────────────────────────────────

TOOL_CATEGORIES = [
    "knowledge",    # search company profiles — plays the role of ENABLE_TOOLS
    "memory",       # persistent preferences — plays the role of ENABLE_MEMORY
]

SUBAGENTS = [
    "researcher",   # gathers info — plays the role of ENABLE_SUBAGENTS
    "verifier",     # fact-checks claims — the fact_checker analogue
]


# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
#
# In the guided demo this was hardcoded in agent.py. Here it's yours to edit.
# The starting prompt below is close to BASE_SYSTEM_PROMPT from the guided demo
# — try changing it and seeing what shifts.
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a research assistant that prepares concise, \
well-sourced company briefings for a busy executive.

When asked to prepare a briefing on a company:
- Search the knowledge base for current information
- Lead with what matters most for a meeting: recent moves, financial position, \
things worth bringing up
- Be specific — cite dates, numbers, and sources when you have them
- Keep it tight — the executive has 90 seconds to read before walking in

Delegate research to the researcher sub-agent and have the verifier check \
key claims before they land in the final briefing."""


DEFAULT_TASK = (
    "Prepare a briefing on Tinplate Merchant Systems for my meeting tomorrow. "
    "I want to understand their recent product moves and financial position."
)


# ──────────────────────────────────────────────────────────────────────────────
# KNOBS
# ──────────────────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-6"
VERBOSITY = "verbose"
MAX_TURNS = 30


# ══════════════════════════════════════════════════════════════════════════════
DATA_DIR = Path(__file__).parent / "data"
