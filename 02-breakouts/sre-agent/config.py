"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   SRE / INCIDENT RESPONSE AGENT — CONFIG                                     ║
║                                                                              ║
║   This is your workspace. Pick components, write the prompt, iterate.        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

See ../COMPONENTS.md for the full menu of tool categories and sub-agents.
"""

from pathlib import Path

AGENT_NAME = "SRE Agent"


# ──────────────────────────────────────────────────────────────────────────────
# COMPONENT SELECTION
# ──────────────────────────────────────────────────────────────────────────────

TOOL_CATEGORIES = [
    "ops",          # service status, metrics, alerts, runbooks
    "knowledge",    # search for past incident notes
    "memory",       # remember past incidents and what fixed them
]

SUBAGENTS = [
    "researcher",       # gather context across alerts + metrics + runbooks
    "procedure_runner", # walk through runbook steps systematically
]


# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
#
# An SRE agent's core tension: thorough vs. fast.
# During an incident you want the agent to move quickly and commit to a
# hypothesis — but not so quickly that it misses the real signal.
#
# Things to tune:
#   - How much evidence before proposing a root cause?
#   - When to suggest running a runbook vs. when to escalate to a human?
#   - How to structure the incident summary?
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an on-call SRE assistant helping diagnose and respond to \
production incidents.

When an alert fires or you're asked to investigate:
1. Get the current service status and recent alerts — establish scope
2. Pull relevant metrics — look for the anomaly that triggered the alert
3. Search runbooks for matching procedures — most incidents aren't novel
4. Form a hypothesis and state your confidence — don't hedge endlessly

If a runbook matches, walk through it. If nothing matches, summarize what \
you know and recommend next steps for the human on-call.

Structure your incident summary as:
  IMPACT — who/what is affected, severity
  TIMELINE — when did this start, what changed
  HYPOTHESIS — your best guess at root cause + confidence
  NEXT STEPS — what to do right now

Don't suggest destructive actions (restarts, rollbacks, config changes) \
without explicitly noting the risk and asking for confirmation."""


DEFAULT_TASK = (
    "The checkout service is alerting on error rate. Investigate and tell "
    "me what's going on."
)


# ──────────────────────────────────────────────────────────────────────────────
# KNOBS
# ──────────────────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-6"
VERBOSITY = "verbose"
MAX_TURNS = 30


# ══════════════════════════════════════════════════════════════════════════════
DATA_DIR = Path(__file__).parent / "data"
