## Overview

Your agent is deployed (Lab 2) and remembers users (Lab 3). The last rung of the ladder makes it **observable**: you'll *see* exactly what your agent does on every request — which tools it called, how long each step took, how many tokens it used, and where things went wrong — in the **Amazon CloudWatch GenAI Observability** dashboard.

The best part: this needs **zero agent code changes**. The AgentCore runtime **auto-instruments** your agent with OpenTelemetry — it's been emitting traces since Lab 2 (`enableOtel` was already on). Lab 4 is about flipping the remaining switches that route those traces to CloudWatch, and learning to *read* them.

A production agent you can't see into is a production agent you can't trust or debug. Observability is what lets you operate it for real.

Older AgentCore examples hand-built OpenTelemetry spans in agent code. That's no longer necessary for runtime-hosted agents — the runtime instruments them for you. You'll *read* the spans it emits, not write them.

## Learning objectives

By the end of this lab, you will be able to:

- Explain why production agents need tracing
- Enable the switches that route your agent's traces to CloudWatch
- Read a trace: the span waterfall, tool calls, tokens, and session correlation
- View agent traces and token/cost data in the CloudWatch GenAI Observability dashboard

## Why observability?

When an agent runs autonomously through a multi-step loop, a single "the answer looks wrong" tells you almost nothing. Observability turns that black box into a glass box:

- **Trace waterfall** — every step and tool call, for debugging
- **Token & cost tracking** — know what each invocation costs
- **Session correlation** — group everything by user/session for support
- **Latency & errors** — spot slow steps and error rates

A production agent you can't see into is one you can't trust or operate.

## Prerequisites

- Labs 1–2 completed (you have a deployed agent; Lab 3's memory is optional here)
- The `agentcore` CLI and a CDK-bootstrapped account/region (same as Lab 2)

Deploy is the same cloud Container build as Lab 2. The only genuinely new setup is enabling **CloudWatch Transaction Search** once at the account level.

## The three switches

Getting a trace into CloudWatch requires **three** things to be true — and the workshop has already handled two of them for you:

| Switch | What it does | Status |
| --- | --- | --- |
| **1\. Transaction Search** (account-level) | Makes spans *searchable* in CloudWatch (they land in `/aws/spans`) | You enable it once (an idempotent script) |
| **2\. The container emits spans** | The image runs under `opentelemetry-instrument` (ADOT) + `enableOtel`, so the agent produces OTEL spans | ✅ Already on since Lab 2 |
| **3\. The runtime delivers spans** | A per-runtime **Tracing** toggle routes the emitted spans to CloudWatch | You flip it once in the console |

> Two distinct things have to be true: the agent must **emit** spans (switch 2) *and* the runtime must be told to **deliver** them (switch 3). Account-level Transaction Search (switch 1) makes them searchable. Miss any one and the dashboard stays empty.

## The one manual step: the Tracing toggle

Switches 1 and 2 are automated. Switch 3 is **a one-time console action**, because AgentCore *runtime* resources don't yet expose a CLI or `agentcore.json` field for trace delivery:

> **AgentCore → Agent Runtime →** your agent (name starts with `cos`) **→ Tracing → Edit → Enable → Save.**

Once enabled, the agent's spans flow to the `/aws/spans` log group and appear in the GenAI Observability dashboard. You only do this once per runtime.

## What you'll see in a trace (reading, not writing)

The runtime emits spans following **OpenTelemetry GenAI semantic conventions** — that's what lets the dashboard render them as an agent trace:

```
invoke_agent cos                         ← top-level span for one request
├── gen_ai.operation.name = "invoke_agent"
├── gen_ai.usage.input_tokens / output_tokens
├── session.id = "<your session id>"     ← groups invocations in the same conversation
└── execute_tool <name>                  ← one child span per tool the agent used
    ├── Bash  (ran a script)
    ├── Read  (read financial_data / CLAUDE.md)
    └── Task  (delegated to a subagent)
```

You **read** these conventions to interpret a trace; the runtime writes them for you. Pass a **session id** when you invoke and the dashboard groups related calls into one conversation.

## CloudWatch dashboard access

```
https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#/gen-ai-observability/agent-core/agents
```

**What you'll see:**

1. **Agent list** — all deployed agents
2. **Session view** — invocations grouped by session
3. **Trace view** — the detailed span waterfall
4. **Metrics** — token usage, latency, error rates

## Hands-on exercise

You can also view the code on [GitHub](https://github.com/aws-samples/sample-agentic-ai-with-claude-agent-sdk-and-amazon-bedrock-agentcore/tree/main/foundations/build-an-ai-chief-of-staff/module-4-observability) .

1. If you haven't already, open the **Module4CodeEditorURL** from [Event Outputs](https://prod.workshops.aws/event/dashboard/en-US) to launch VS Code with the workshop repository.
2. In your Code Editor, open the notebook at:

```bash
foundations/build-an-ai-chief-of-staff/module-4-observability/module-4-observability.ipynb
```

3. **Enable Transaction Search** (switch 1) — run the idempotent helper once at the account level.
4. **Deploy** the agent (`agentcore deploy -y`) — it already emits spans (switch 2, on since Lab 2).
5. **Enable the Tracing toggle** (switch 3) in the console for your deployed runtime.
6. **Invoke** the agent a couple of times, passing a **session id** to correlate the conversation.
7. **View the traces** in the CloudWatch GenAI Observability dashboard (allow a couple of minutes to index), then `agentcore remove` the runtime.

It's an account-level, one-time setting — not per-deployment — and there's no charge for leaving it enabled at low indexing sampling.

## Key takeaways

1. **Zero agent code** — the AgentCore runtime auto-instruments your agent; it's been emitting OTEL spans since Lab 2.
2. **Three switches, all required** — account-level **Transaction Search**, the **container emitting** spans (already on), and the per-runtime **Tracing toggle** (a one-time console click).
3. **GenAI semantic conventions** (`gen_ai.*`, `session.id`) are what let the dashboard render the trace waterfall, tokens, and tool calls.
4. **Pass a session id** on invoke to correlate a conversation in the dashboard.

You've climbed the whole ladder: your agent is built, deployed, stateful, and observable.

Want to apply all of this to a real enterprise scenario? Continue to the optional Advanced chapter (Text-to-SQL on Athena). Otherwise, head to the Conclusion for a recap and cleanup.
