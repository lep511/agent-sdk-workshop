"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   BREAKOUT TEMPLATE — COPY THIS TO 02-breakouts/your-name/                   ║
║                                                                              ║
║   See ../COMPONENTS.md for the full component menu.                          ║
║   See extend/add-a-breakout.md for the full walkthrough.                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pathlib import Path

AGENT_NAME = "My Agent"


# ──────────────────────────────────────────────────────────────────────────────
# COMPONENT SELECTION — see ../COMPONENTS.md for options
# ──────────────────────────────────────────────────────────────────────────────

TOOL_CATEGORIES: list[str] = [
    # "knowledge",
    # "schedule",
    # "support",
    # "ops",
    # "code",
    # "memory",
]

SUBAGENTS: list[str] = [
    # "researcher",
    # "summarizer",
    # "classifier",
    # "verifier",
    # "writer",
    # "procedure_runner",
]


# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a ..."""


DEFAULT_TASK = "What would you like to do?"


# ──────────────────────────────────────────────────────────────────────────────
# KNOBS
# ──────────────────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-6"
VERBOSITY = "verbose"
MAX_TURNS = 30


# ══════════════════════════════════════════════════════════════════════════════
DATA_DIR = Path(__file__).parent / "data"
