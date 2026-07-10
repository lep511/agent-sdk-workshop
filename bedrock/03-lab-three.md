## Overview

At the end of Lab 2 you hit a wall: your deployed agent **forgets you between calls**. Invoke it twice and the second request starts from zero. For a real product, that's a dealbreaker — users expect to be remembered.

In this lab you fix that with **Amazon Bedrock AgentCore Memory**. You'll give your deployed agent the ability to remember across invocations and across sessions — without building or operating any memory infrastructure yourself, and **without rewriting the agent**: `build_agent_options()` stays the single source of truth; memory is layered on in the thin entrypoint.

This is where "it forgot me" becomes "it remembers me." Same agent, same deployment — now with memory.

Scope: single-tenant

To keep the focus on *how memory works*, this lab uses one fixed user (`actorId = "techstart-cos"`). Production multi-tenant memory — deriving the actor from inbound identity so each user gets an isolated namespace — is a deliberate next step, not covered here.

## Learning objectives

By the end of this lab, you will be able to:

- Explain the difference between **short-term** and **long-term** memory in AgentCore
- Create a managed **Memory resource**
- Write conversation turns to memory and **retrieve** relevant context before responding
- Scope memory correctly with **actor** and **session** identifiers
- Demonstrate **cross-session recall**: the agent remembers a returning user

## Why AgentCore Memory?

You *could* build memory yourself — a database, an embedding pipeline, retrieval logic, expiry policies, isolation between users. AgentCore Memory gives you all of that as a managed service, so you keep full control over *what* is remembered without operating the plumbing.

AgentCore Memory has two layers:

| Layer | What it is | Lifespan |
| --- | --- | --- |
| **Short-term memory** | Raw turn-by-turn **events** within a session (the conversation so far) | Within a session |
| **Long-term memory** | Insights **extracted** from those events and persisted, retrievable by meaning | Across sessions |

Long-term memory is produced by **strategies** that run in the background to distil events into reusable knowledge. AgentCore offers several (Semantic facts, Summarization, User preference, Episodic); this lab enables **two**:

- **Semantic** — extracts durable *facts* (e.g. "the raise target is $X")
- **User preference** — captures *how the user likes things* (e.g. "report runway in weeks")

Short-term events are available **immediately**. Long-term extraction is **asynchronous** — facts and preferences only become retrievable a minute or two after a turn is written. So this lab's **live** cross-session recall rides on the **short-term** layer (replaying the actor's prior-session events), while the **long-term** layer is the "it *learned* about you over time" beat you inspect after a natural gap.

## Two key ideas: actor and session

Memory is scoped by two identifiers, and getting them right is what makes recall correct:

- **`actorId`** — *who* the memory belongs to (e.g., a specific user). This is what lets the agent remember *you* specifically, across all your sessions.
- **`sessionId`** — *which conversation* an event belongs to. Short-term memory groups events by session; long-term insights are retrievable across sessions for the same actor.

> The "it remembers me" magic comes from the **actor**: when the same user returns in a brand-new session, the agent retrieves what it learned about that actor before.

## Prerequisites

- Lab 2 completed (you have a deployed agent)
- The `agentcore` CLI and a CDK-bootstrapped account/region (same as Lab 2)

Memory is declared in `agentcore/agentcore.json` (`memories[]`). When you `agentcore deploy`, the CDK provisions the Memory resource *alongside* the runtime, **auto-wires the memory IAM** onto the execution role, and injects the memory id as an env var (`MEMORY_COSMEMORY_ID`) that the agent reads. You don't write any IAM or boto3 setup.

## What this lab does

```
Deployed agent (Lab 2, stateless)
           │
           ▼
1. Declare a Memory resource in agentcore.json, then deploy
   (provisions runtime + memory together; auto-wires IAM)
           │
           ▼
2. On each turn: RECALL prior context, run, then RECORD the turn
   (a thin memory/session.py the entrypoint calls — agent unchanged)
           │
           ▼
3. Prove it: a brand-new session recalls what an earlier one said
   (and an honest A/B with memory off shows the difference)
           │
           ▼
Agent now remembers the user across calls and sessions
```

## Step 1 — Declare the Memory resource

Memory lives in `agentcore.json` under `memories[]`: one memory named `CosMemory` with the two long-term strategies (SEMANTIC facts + USER\_PREFERENCE) and **actor-scoped namespaces** (`users/{actorId}/...`). `agentcore deploy` provisions it with the runtime — no separate setup step.

## Step 2 — Layer memory onto the agent (without forking it)

The agent itself is unchanged. Two thin pieces do the work: a `memory/session.py` helper exposing `retrieve_context()` (turn start) and `record_turn()` (turn end), and a few lines in the entrypoint that **recall** relevant context before the turn — injecting it through the additive `system_prompt_suffix` — and **record** the turn after. If memory isn't configured (e.g. a local run), the helper degrades gracefully and the agent simply behaves like Lab 2.

## Step 3 — Prove cross-session recall

You invoke as the same actor across two **separate** sessions. Session A states a fact; a brand-new Session B — sharing no transcript — recalls it. Because the live recall rides on **short-term** events (instant), there's no waiting on extraction. An **honest A/B** (the same prompt with memory turned off) confirms the recall comes from memory, not prompt phrasing.

## Hands-on exercise

You can also view the code on [GitHub](https://github.com/aws-samples/sample-agentic-ai-with-claude-agent-sdk-and-amazon-bedrock-agentcore/tree/main/foundations/build-an-ai-chief-of-staff/module-3-memory) .

1. If you haven't already, open the **Module4CodeEditorURL** from [Event Outputs](https://prod.workshops.aws/event/dashboard/en-US) to launch VS Code with the workshop repository.
2. In your Code Editor, open the notebook at:

```bash
foundations/build-an-ai-chief-of-staff/module-3-memory/module-3-memory.ipynb
```

3. Review the `memories[]` config and the thin `memory/session.py` layer.
4. Run `agentcore deploy -y` — provisions the runtime **and** the `CosMemory` resource.
5. **Session A:** Tell the agent something only this conversation knows — a **$42.5M** raise target (the company `CLAUDE.md` hardcodes a **$30M** Series B, so a later recall can *only* be memory).
6. **Session B:** Open a brand-new session and watch it recall the **$42.5M** target.
7. **Prove it:** Re-run with memory off — it forgets. Honest A/B.
8. Inspect the **long-term** facts/preferences the service extracted in the background, then `agentcore remove` both resources.

AgentCore silently drops shorter ones, which would break short-term recall.

## Before vs. after

|  | Lab 2 (no memory) | Lab 3 (with memory) |
| --- | --- | --- |
| Same session, follow-up | Forgets the previous turn | Remembers it |
| New session, returning user | Total stranger | Recalls what it learned before |
| Infrastructure you manage | — | Still none — fully managed |

## Key takeaways

- AgentCore Memory provides **short-term** (events, immediate) and **long-term** (extracted, async) memory as a managed service — and `agentcore deploy` **auto-wires the IAM** and injects the memory id.
- The pattern is simple: **recall relevant context, run, record the turn** — layered on without forking the agent (`build_agent_options()` stays the source of truth).
- **`actorId`** ties memory to a user; **`sessionId`** ties events to a conversation. Live cross-session recall rides on short-term events; long-term is the "learned over time" layer.
- An **honest A/B** (memory on vs. off, same prompt) is how you prove the recall is real.
- Your agent now remembers users across sessions — the Lab 2 limitation is solved.

Continue to the next page to add observability.
