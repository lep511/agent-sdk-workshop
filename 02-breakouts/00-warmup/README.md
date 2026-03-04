# Warmup — The Bridge

**Same task. Same companies. New interface.**

This is the company-briefing agent from the guided demo, but assembled the breakout way. Instead of flipping three booleans, you pick tool categories, pick sub-agents, and edit the system prompt directly.

The point: feel the transition from "guided tour" to "Lego assembly" on a domain you already know, before switching to a new one (support, SRE, etc.).

---

## How to run

```bash
./workshop breakout 00-warmup
```

---

## What to try

1. **Run the starting config** — should feel like Stage 3 of the guided demo (tools + subagents + memory all on).
2. **Remove `"memory"` from `TOOL_CATEGORIES`** — re-run. Recognize the Stage 2 behavior?
3. **Empty out `SUBAGENTS`** — re-run. Recognize Stage 1?
4. **Rewrite `SYSTEM_PROMPT`** — in the guided demo this was locked in `agent.py`. Now it's yours.

---

## The pattern connection

Open these two files side by side:

| Guided demo | Breakouts |
|---|---|
| `01-guided-demo/agent.py:build_options()` | `02-breakouts/_shared/agent_base.py:_build_options()` |

**They're the same pattern.** The guided demo's version checks three booleans and sets SDK options directly. The breakouts' version reads your lists and translates them to SDK options. Both end up building the same `ClaudeAgentOptions` shape.

Once you see that, you're ready for the real breakouts. Pick one:
[`chief-of-staff`](../chief-of-staff/) · [`customer-support`](../customer-support/) · [`sre-agent`](../sre-agent/) · [`account-intelligence`](../account-intelligence/) · [`freeform`](../freeform/)
