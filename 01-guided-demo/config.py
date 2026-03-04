"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   THIS IS THE ONLY FILE YOU NEED TO EDIT DURING SESSION 2.                   ║
║                                                                              ║
║   Between each exercise, you'll flip one more switch from False → True       ║
║   and re-run the agent to see what changes.                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ──────────────────────────────────────────────────────────────────────────────
# STAGE 1 — TOOLS
# ──────────────────────────────────────────────────────────────────────────────
# With tools OFF, the agent can only answer from its training data. It has no
# way to look anything up — you're just chatting with a very knowledgeable
# person who hasn't read the news since training cutoff.
#
# Flip this to True and the agent gains three research tools:
#   • search_company_news(company, topic)
#   • get_company_financials(company)
#   • get_recent_press_releases(company)
#
# Try asking for the same briefing before and after. The difference is night
# and day — now the agent *looks things up* instead of guessing.
ENABLE_TOOLS = False


# ──────────────────────────────────────────────────────────────────────────────
# STAGE 2 — SUB-AGENTS
# ──────────────────────────────────────────────────────────────────────────────
# With sub-agents OFF, the main agent does everything itself — research,
# fact-checking, synthesis — all in one context window. It works, but each
# task competes for the same attention.
#
# Flip this to True and the main agent becomes an orchestrator. It delegates:
#   • A "researcher" sub-agent handles deep information gathering
#   • A "fact_checker" sub-agent cross-references claims before they land
#     in your briefing
#
# Watch for the sub-agent spawn/return messages in the console. The main
# agent's job shifts from "do everything" to "coordinate specialists."
#
# (Requires ENABLE_TOOLS = True — sub-agents need tools to be useful.)
ENABLE_SUBAGENTS = False


# ──────────────────────────────────────────────────────────────────────────────
# STAGE 3 — MEMORY
# ──────────────────────────────────────────────────────────────────────────────
# With memory OFF, every run starts from zero. Tell the agent "I prefer
# bullet points" and it'll forget the moment you close the terminal.
#
# Flip this to True and the agent gains a persistent memory file
# (memory_store.json) that survives between runs. It can:
#   • Remember your stated preferences ("keep briefings under 300 words")
#   • Recall what it told you last time ("as I mentioned in the prior briefing...")
#   • Build on prior work instead of starting over
#
# Try this: run a briefing, mention a preference, then run again. It should
# acknowledge what it learned about you.
ENABLE_MEMORY = False


# ──────────────────────────────────────────────────────────────────────────────
# ADVANCED — you probably won't touch these during the guided session, but
# feel free to experiment during breaks.
# ──────────────────────────────────────────────────────────────────────────────

# Which Claude model to use. "claude-sonnet-4-6" is fast and cheap — great
# for a workshop. Try "claude-opus-4-6" if you want to compare quality.
MODEL = "claude-sonnet-4-6"

# Console output verbosity:
#   "normal"  — just the agent's text responses
#   "verbose" — also show tool calls, sub-agent spawns, cost breakdown
VERBOSITY = "verbose"

# The default request sent to the agent on each run. You can override this
# at the prompt when the agent starts, or change it here.
DEFAULT_TASK = (
    "Prepare a briefing on Tinplate Merchant Systems for my meeting tomorrow. "
    "I want to understand their recent product moves and financial position."
)


# ──────────────────────────────────────────────────────────────────────────────
# STRETCH GOALS — if you're ahead of the group, try these between stages.
# No setup needed, just questions to poke at.
# ──────────────────────────────────────────────────────────────────────────────
#
# Stage 0 → Stage 1:
#   • Ask about "Apple" or "Google" (not in mock_data/). How does the agent
#     handle not finding data? Does it admit it, or hallucinate?
#
# Stage 1 → Stage 2:
#   • Try "compare Tinplate and Bucklefern Commerce Holdings on financial health."
#     Do sub-agents spawn in parallel? Check the console for multiple Task
#     calls in the same turn.
#   • Open subagents.py and change the fact_checker's model from "haiku"
#     to "sonnet". Re-run. Does quality change?
#
# Stage 2 → Stage 3:
#   • Tell the agent a weird preference ("always end briefings with a
#     haiku"). Exit. Re-run. Did it stick?
#   • Run ./workshop reset to clear memory, then re-run. Does the agent
#     notice it forgot something?
#
# Any stage:
#   • Set VERBOSITY = "normal" and re-run. What information do you lose?
#   • Swap MODEL to "claude-opus-4-6". Same prompt, bigger model — does
#     the briefing quality noticeably change?
#   • Run ./workshop demo --show-prompt to see the full assembled context
#     the SDK is sending to the model. Compare at different stages.
#   • (SDK v0.1.41+) Add EFFORT = "high" here and pass it to the
#     ClaudeAgentOptions in agent.py:build_options(). Does a harder
#     question get a better answer?