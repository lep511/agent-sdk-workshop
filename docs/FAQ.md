# FAQ

Common questions about the SDK and this workshop.

---

### How is the Agent SDK different from just using the Messages API directly?

You *can* build everything in this workshop with the raw Messages API. The SDK gives you:

- **The agentic loop for free.** You don't write the `while stop_reason == "tool_use"` loop. You subscribe to a message stream.
- **Simpler tool definition.** `@tool` decorator + Python types instead of hand-written JSON Schema.
- **Sub-agents as a primitive.** The `Task` tool and `AgentDefinition` pattern don't exist in the raw API — you'd build your own.
- **Lifecycle hooks.** `PreToolUse`, `PostToolUse`, `UserPromptSubmit` fire automatically — no manual interception.
- **Session management, retry, streaming** out of the box.

Rough LOC reduction: ~50% for equivalent behavior. See [`docs/CHEATSHEET.md`](./CHEATSHEET.md) for the full pattern reference.

---

### What's the difference between an agent and a sub-agent?

| | Main agent | Sub-agent |
|---|---|---|
| Who defines it | You, via `ClaudeAgentOptions` | You, via `AgentDefinition` |
| Who invokes it | You, via `client.query()` | The main agent, via `Task(subagent_type="...", prompt="...")` |
| Context window | The one you're watching | Its own, isolated |
| Sees conversation history? | Yes | No — only the prompt passed to `Task` |

The main agent is the one you talk to. Sub-agents are its workers — spun up on demand, run to completion, return one answer, discarded.

---

### What's the difference between a tool and a hook?

| | Tool | Hook |
|---|---|---|
| Who triggers it | The model, mid-turn | The SDK, on lifecycle events |
| Model aware of it? | Yes — in the tool list | No — invisible |
| Use for | Capabilities the agent needs | Guardrails, context injection, logging, blocking |

A tool is something the model *chooses* to call. A hook is a callback that fires *automatically* when something happens (user submits a prompt, tool is about to run, etc.).

The memory system in Stage 3 uses both: a **tool** to let the model choose what to save, a **hook** to automatically inject saved memories into every new conversation.

---

### Why are all the tools fake / mock data?

Two reasons:

1. **The workshop is about SDK patterns, not integrations.** If we used real APIs, half the session would be "get your Salesforce/Jira/whatever credentials working." Mock data lets you focus on the interesting part.
2. **Reliability.** Real APIs flake, rate-limit, change. A workshop that depends on third-party uptime is a workshop waiting to go sideways.

The `@tool` contract is the same either way. In production you'd swap the mock implementation for a real API call — the agent code doesn't change.

---

### Can I use a different model?

Yes. Change `MODEL` in `config.py` to any model ID your API key has access to:

- `claude-sonnet-4-6` — default, fast and cheap
- `claude-opus-4-6` — slower and pricier but highest quality
- `claude-haiku-4-5` — fastest, good for sub-agents

You can also set different models for sub-agents vs. the main agent (the starter sub-agent configs all use `"haiku"`).

---

### How much does a workshop session cost?

Roughly: the four-stage guided demo at default settings runs **under $0.10** for sonnet, maybe **$0.30–0.50** for opus. The SDK prints the cost after each turn (`[done — 3 turn(s), $0.0234]`).

Breakout iteration depends on how much you run. Budget a dollar or two for an active session.

---

### Can I run sub-agents in parallel?

Yes, but it's **prompt-driven, not code-driven.** The model spawns sub-agents by calling the `Task` tool. If the model emits multiple `Task` calls in a single turn, the SDK runs them in parallel.

To get parallelism, your system prompt needs to tell the orchestrator to do this: *"When researching multiple topics, spawn a separate researcher for each in the same turn — don't wait for one to finish before starting the next."*

---

### Why doesn't `ENABLE_MEMORY` give the agent memory of the current conversation?

It does — but that's not the thing `ENABLE_MEMORY` unlocks.

**Within-session memory** (ask a follow-up, it remembers the context) works at **every stage** because `ClaudeSDKClient` preserves conversation history while connected. You get this for free with no toggle.

**Cross-session memory** (close the terminal, run again tomorrow, it still knows your preferences) is what Stage 3 adds. That's the part that needs a persistence layer.

---

### How do I evaluate whether my agent is actually good?

Great question — and the biggest gap folks flagged in the last workshop. Short answer for now:

1. **Write down 5–10 test prompts** that cover what the agent should handle
2. **Run them after each config change** and score pass/fail manually
3. **Look for regressions** — did enabling a sub-agent make something worse?

The SDK doesn't have a built-in eval harness yet. For production agents, most teams build a simple harness: a list of (prompt, expected_behavior) pairs, run them, have a model judge the outputs. We're working on better guidance here.

---

### Can I run this with Claude Code instead of the SDK directly?

Not for this workshop — the exercises are specifically about the SDK's Python API. But the Agent SDK and Claude Code share the same underlying primitives (tools, sub-agents, hooks), so the mental models transfer directly.

---

### I want to build something for real after this. Where do I start?

1. The [SDK README](https://github.com/anthropics/claude-agent-sdk-python) and its `examples/` directory
2. The [cookbook agents](https://github.com/anthropics/claude-cookbooks/tree/main/claude_agent_sdk) — production-shaped reference implementations
3. The breakout you worked on here — swap the mock tools for real integrations and you've got a real agent
