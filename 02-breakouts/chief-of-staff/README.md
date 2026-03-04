# Chief of Staff Agent

Build an agent that manages an executive's calendar, prepares meeting briefings, and drafts communications — the kind of workflow automation that lets one senior person operate at the leverage of three.

---

## The scenario

You're the chief of staff for a startup CEO with a board meeting tomorrow. The mock data includes:

- **Calendar** — the next few days of meetings with context-rich notes
- **Documents** — board pre-read questions, Q1 priorities draft, account notes for an upcoming customer call
- **Knowledge base** — exec communication preferences, board protocol, email templates

Your agent needs to pull the right information together and produce something the CEO can actually use — with 90 seconds of reading, not 20 minutes of back-and-forth.

---

## How to run

From the repo root:

```bash
./workshop breakout chief-of-staff
```

Press Enter for the default task (board meeting prep) or type your own.

---

## What to tinker with

**`config.py` is your workspace.** Two things to change:

### 1. Component selection

Starting config enables `schedule`, `knowledge`, `memory` tools and `summarizer`, `writer` sub-agents. Try:

- **Add the `verifier` sub-agent** — does the agent catch when it's about to put something in a briefing that contradicts the docs?
- **Remove `memory`** — how much worse does the agent get at remembering the exec's stated preferences between runs?
- **Remove sub-agents entirely** — does the agent produce messier drafts when it can't delegate to `writer`?

### 2. The system prompt

This is where most of the improvement comes from. Try:

- **Add output structure:** "Briefings must have three sections: Context (what's happening), Ask (what decision is needed), Recommendation (your take)."
- **Add guardrails:** "Never draft an email to a board member directly — all board comms go through the GC's assistant. If asked to email the board, draft it but flag the routing."
- **Add prioritization:** "When multiple docs are relevant, lead with the one the exec hasn't seen yet."

Run the agent after each change. The iteration loop is: edit prompt → run → read output → edit prompt.

---

## Good test prompts

Beyond the default, try:

- "Prep me for the Ironvane Freight Systems call on Thursday."
- "Draft a follow-up email to Morgan Lee after the Ironvane call assuming it went well."
- "What's the hardest board question I'll get tomorrow and what's my answer?"
- "I prefer one-line bullets, not full sentences. Remember that." *(then run again)*

---

## Reference

The cookbook has a more elaborate [chief_of_staff_agent](https://github.com/anthropics/claude-cookbooks/tree/main/claude_agent_sdk/chief_of_staff_agent) with financial modeling sub-agents and compliance checks — worth studying after the workshop.
