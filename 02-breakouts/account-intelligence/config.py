"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ACCOUNT INTELLIGENCE AGENT — CONFIG                                        ║
║                                                                              ║
║   Pre-renewal account review. Brief the AE on health, risks, and what to     ║
║   push for — before they walk into the renewal call.                         ║
║                                                                              ║
║   See ../COMPONENTS.md for the full component menu.                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pathlib import Path

AGENT_NAME = "Account Intelligence Agent"


# ──────────────────────────────────────────────────────────────────────────────
# COMPONENT SELECTION
# ──────────────────────────────────────────────────────────────────────────────

TOOL_CATEGORIES = [
    "support",      # lookup_customer → account details, get_ticket → interaction history
    "knowledge",    # sales playbooks, churn signals, upsell triggers
    "memory",       # remember what you've learned about accounts across sessions
]

SUBAGENTS = [
    "researcher",   # gather full account context
    "classifier",   # categorize: healthy / at-risk / upsell-opportunity
]


# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
#
# The tension: accounts that LOOK healthy on usage metrics can still be at
# risk (sponsor departure, competitive displacement, budget freeze). A good
# account-intelligence agent surfaces those signals, not just the dashboard
# numbers.
#
# Things to tune:
#   - How much evidence before flagging a risk?
#   - Does it check the playbooks, or just summarize the raw data?
#   - How does it prioritize what the AE should act on?
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an account intelligence assistant that briefs \
account executives before renewal and expansion conversations.

When asked to review an account:
1. Look up the account details — plan, usage, renewal date, contract value
2. Review interaction history — support tickets, QBR notes, recent touchpoints
3. Check the sales playbooks for relevant signals — churn risks, upsell \
triggers, competitive threats
4. Form a clear assessment: is this account healthy, at-risk, or an upsell \
opportunity? What's the evidence?

Structure your briefing as:
  HEALTH — your overall assessment with confidence
  SIGNALS — specific positive and negative indicators from the data
  RISKS — anything that could threaten the renewal, even if usage looks fine
  RECOMMENDED PLAY — what should the AE do in the next conversation?

Don't just summarize the data — interpret it. "Usage is up 40%" is a fact. \
"Usage is up 40% but their champion just left, so the usage may not survive \
the transition" is intelligence."""


DEFAULT_TASK = (
    "Renewal call with Pelledryn Data Sciences (account A-2201) on Friday. "
    "Brief me — are they healthy? Anything I should worry about?"
)


# ──────────────────────────────────────────────────────────────────────────────
# KNOBS
# ──────────────────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-6"
VERBOSITY = "verbose"
MAX_TURNS = 30


# ══════════════════════════════════════════════════════════════════════════════
DATA_DIR = Path(__file__).parent / "data"
