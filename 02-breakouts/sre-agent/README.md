# SRE / Incident Response Agent

Build an on-call assistant that investigates production alerts, correlates metrics with deploys, and walks through runbooks — the first five minutes of incident response, automated.

---

## The scenario

The **checkout service** is alerting on error rate. A deploy went out 20 minutes ago. There's a runbook that covers exactly this situation. The agent's job is to connect those dots and tell the human on-call what to do.

Mock data includes:
- **Service status** — health state, dependencies, recent deploys
- **Alerts** — recent fires, including the timeline that leads to "deploy at 11:42 → error spike at 12:03"
- **Metrics** — query_metrics generates plausible time-series data, with a deliberate anomaly in checkout/error_rate
- **Runbooks** — including RB-001 which matches this scenario
- **Past post-mortems** — so the agent can check if this has happened before

---

## How to run

From the repo root:

```bash
./workshop breakout sre-agent
```

---

## What to tinker with

### Component selection

- **Remove `procedure_runner`** — does the agent still walk through runbook steps systematically, or does it skip around?
- **Remove `knowledge`** — now it can't check past post-mortems. Does it miss the pattern from the Feb 14 incident?

### The system prompt — the interesting part

The checkout incident is designed to be solvable: deploy → error spike → runbook RB-001 → rollback recommendation. The question is whether your prompt gets the agent to **find and commit to** that path, or whether it hedges and says "could be many things."

Things to try:
- **Force timeline-first:** "Always establish a timeline before hypothesizing. What happened, in what order?"
- **Bias toward deploys:** "When in doubt, suspect the most recent deploy."
- **Structured output:** the starter prompt has an IMPACT/TIMELINE/HYPOTHESIS/NEXT STEPS template. Try removing it — does the output get muddier?
- **Confidence calibration:** "State confidence as high/medium/low and say what evidence would change your mind."

### Good test prompts

- The default: "checkout is alerting on error rate, investigate"
- "Is there a runbook for this? Walk me through it."
- "Has something like this happened before?"
- "What would you do if the rollback doesn't fix it?"

---

## Reference

The cookbook has an [observability_agent](https://github.com/anthropics/claude-cookbooks/tree/main/claude_agent_sdk/observability_agent) with real GitHub integration — a good next step after the workshop.
