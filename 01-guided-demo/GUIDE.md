# Guided Demo — Stage-by-Stage Walkthrough

You're going to run the **same agent four times**, flipping one switch between each run, and watch it get progressively better at the same job.

**The task:** prepare a company briefing. You ask the agent to brief you on a (fictional) company before a meeting. At Stage 0 it guesses. By Stage 3 it's searching data sources, delegating fact-checking to a sub-agent, and remembering your preferences from last time.

**The only file you edit:** [`config.py`](./config.py). Three boolean switches.

```bash
./workshop demo     # from the repo root, every time
```

---

## Stage 0 — Basic Chat

**Config:** everything `False` · **Primitive:** `ClaudeSDKClient` + `system_prompt`

### What to do

1. Make sure all three toggles in `config.py` are `False` (they are by default).
2. Run `./workshop demo` (or `python 01-guided-demo/agent.py`).
3. At the prompt, press Enter to use the default request (a briefing on Tinplate Merchant Systems).

### What to observe

The agent will **try** to produce a briefing. It'll be articulate, well-structured, and… probably wrong. Or vague. Or hedged with phrases like "as of my training data" and "I don't have current information about…"

This is the baseline. You're talking to a very capable model with a good system prompt and **zero ability to look anything up**. It knows *how* to write a briefing, it just has nothing recent to put in it.

**Try asking a follow-up** like "what was their Q4 revenue specifically?" — the agent has no way to answer with confidence.

### What's happening under the hood

Open [`agent.py`](./agent.py) and find the `build_options()` function. With all toggles `False`, it returns:

```python
ClaudeAgentOptions(
    model="claude-sonnet-4-6",
    system_prompt=BASE_SYSTEM_PROMPT,
    mcp_servers={},         # ← empty
    allowed_tools=[],       # ← empty
    agents=None,            # ← none
    hooks=None,             # ← none
    permission_mode="bypassPermissions",
)
```

That's it. A model, a system prompt, and nothing else. The SDK still handles the connection lifecycle, streaming, and message parsing — but there's no agentic loop yet because there are no tools to call. The model responds once and it's done.

---

## Stage 1 — Tools

**Config:** `ENABLE_TOOLS = True` · **Primitive:** `@tool` + `create_sdk_mcp_server`

### What to do

1. Open `config.py` and flip the first switch:
   ```python
   ENABLE_TOOLS = True   # ← changed
   ```
2. Re-run `./workshop demo`. Same request as before.

### What to observe

This time you'll see yellow `→ calling ...` lines in the output — that's the agent using its new tools:

```
→ calling mcp__research__search_company_news(company='Tinplate Merchant Systems', topic='product')
  ← tool returned: Recent news for Tinplate Merchant Systems: [2026-02-18] Tinplate Merchant Systems launches...
→ calling mcp__research__get_company_financials(company='Tinplate Merchant Systems')
  ← tool returned: {"company": "Tinplate Merchant Systems", "industry": "Financial Technology"...
```

And the briefing that follows is **actually grounded.** Specific dates, specific dollar figures, recent product launches, all cited. Same question, night-and-day answer.

**Try asking follow-ups** that require cross-referencing — "who did they hire recently and where did that person come from?" The agent will go back to its tools.

### What just happened

Two things got wired into `ClaudeAgentOptions`:

```python
mcp_servers={"research": research_server},   # ← bundle of tools
allowed_tools=[
    "mcp__research__search_company_news",
    "mcp__research__get_company_financials",
    "mcp__research__get_recent_press_releases",
    "mcp__research__get_competitive_landscape",
],
```

Now the SDK runs a **real agentic loop.** Instead of responding once, the model:
1. Sees the tools in its context
2. Decides which to call and with what arguments
3. The SDK executes them locally (in this process, no subprocess)
4. Results go back to the model
5. Repeat until it has what it needs, then write the briefing

You didn't write the loop. You wrote the tools — the SDK handles orchestration.

### Look at the code

Open [`tools.py`](./tools.py). Each tool is a `@tool`-decorated async function:

```python
@tool(
    "search_company_news",                    # name the model sees
    "Search recent news coverage about...",   # tells the model when to use it
    {"company": str, "topic": str},           # input schema (auto-converted to JSON Schema)
)
async def search_company_news(args: dict) -> dict:
    # your logic here — read a DB, call an API, whatever
    return {"content": [{"type": "text", "text": "..."}]}
```

At the bottom of `tools.py`, `create_sdk_mcp_server()` bundles the tools. That's what goes into `mcp_servers`.

---

## Stage 2 — Sub-agents

**Config:** `ENABLE_SUBAGENTS = True` · **Primitive:** `AgentDefinition` + the `Task` tool

### What to do

1. Open `config.py` and flip the second switch (keep the first one on):
   ```python
   ENABLE_TOOLS = True
   ENABLE_SUBAGENTS = True   # ← changed
   ```
2. Re-run `./workshop demo`.

### What to observe

Watch the console for `Task` tool calls. Something like:

```
→ calling Task(subagent_type='researcher', prompt='Find Tinplate Merchant Systems recent product announcements and Q4 financials')
  ← tool returned: [researcher's full findings condensed into one message]
→ calling Task(subagent_type='fact_checker', prompt='Verify: Q4 2025 revenue was $118M, embedded lending launched Feb 2026')
  ← tool returned: CONFIRMED: Q4 revenue $118M (press release Feb 10). CONFIRMED: Tinplate Capital launched Feb 18.
```

The main agent isn't searching anymore — it's **coordinating.** A researcher sub-agent does the digging, a fact-checker verifies key claims before they land in your briefing.

The briefing quality might not feel dramatically different from Stage 1 for a simple request. The gain shows up on **complex requests** — try "compare Tinplate and Bucklefern Commerce Holdings on product velocity and financial health." The main agent can spawn parallel researchers for each company and synthesize their findings without drowning in raw search results.

### What just happened

One more SDK option got populated:

```python
agents={
    "researcher": AgentDefinition(
        description="Gathers raw information about a company...",
        prompt="You are a thorough research analyst...",
        tools=[...research tools...],
        model="haiku",
    ),
    "fact_checker": AgentDefinition(...),
},
allowed_tools=["Task", ...research tools...],
```

Now the main agent has a `Task` tool. When it calls `Task(subagent_type="researcher", prompt="...")`, the SDK:
1. Spins up a **completely isolated conversation** with the researcher's system prompt
2. The researcher has its own tool allowlist, its own model (`haiku` — cheap and fast)
3. The researcher runs to completion — *its* tool calls, *its* back-and-forth, all in *its* context
4. Only the final answer comes back to the main agent

**This is context engineering.** The main agent's context window stays clean. It sees "here's what the researcher found," not the twelve tool calls and three dead ends the researcher took to get there.

### Agents vs. sub-agents — the mental model

| | Main agent | Sub-agent |
|---|---|---|
| **Who defines it** | You, via `ClaudeAgentOptions` | You, via `AgentDefinition` |
| **Who invokes it** | You, via `client.query()` | The main agent, via `Task(...)` |
| **Context window** | The one you're watching | Its own, isolated |
| **Sees conversation history?** | Yes, all of it | No — only the prompt you pass to `Task` |
| **Return value** | Streams to you | Single message back to main agent |

The main agent is the one you're *talking to.* Sub-agents are *its* workers.

### Look at the code

Open [`subagents.py`](./subagents.py). The definitions are about 15 lines each — `description` (when should the orchestrator use this?), `prompt` (the sub-agent's system prompt), `tools` (its allowlist), `model` (optional override).

---

## Stage 3 — Memory & Context

**Config:** `ENABLE_MEMORY = True` · **Primitive:** `hooks` + a persistence tool

### What to do

1. Open `config.py` and flip the third switch:
   ```python
   ENABLE_TOOLS = True
   ENABLE_SUBAGENTS = True
   ENABLE_MEMORY = True   # ← changed
   ```
2. Run `./workshop demo`.
3. During the run, **express a preference.** Something like "I prefer bullet points over paragraphs" or "keep briefings under 200 words." Watch for a `save_memory` tool call.
4. **Exit and run again.** The agent should acknowledge what it learned about you before you say a word.

### What to observe

**First run:** After the briefing, look for a line like:
```
→ calling mcp__memory__save_memory(category='preferences', note='User prefers bullet points over prose paragraphs')
```

**Second run:** Before the agent even starts, you'll see:
```
Loaded memories from previous sessions:
  • [preferences] User prefers bullet points over prose paragraphs  (2026-03-05 14:32)
```

And the briefing it produces should honor that preference — without you having to repeat yourself.

**This persists through terminal restarts.** Open `memory_store.json` to see the raw store. Delete that file (or run `./workshop reset`) to reset.

### What just happened

Two complementary pieces:

**A tool to WRITE memories:**

```python
mcp_servers["memory"] = make_memory_server()
allowed_tools.extend(["mcp__memory__save_memory", "mcp__memory__list_memories"])
```

The agent can now call `save_memory(category, note)` to persist something. Standard tool — same `@tool` decorator pattern from Stage 1.

**A hook to READ memories:**

```python
hooks = {"UserPromptSubmit": [memory_hook]}
```

**Hooks are different from tools.** A tool is something the model *chooses* to call. A hook is a Python callback that **fires automatically on SDK lifecycle events** — the model doesn't know it exists.

The `UserPromptSubmit` hook fires every time a user message is about to be sent to the model. Our hook reads `memory_store.json` and returns:

```python
return {
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "MEMORIES FROM PREVIOUS SESSIONS:\n- [preferences] User prefers bullet points...",
    }
}
```

The SDK weaves `additionalContext` into the system context before the message goes out. So the model sees your preferences as if you'd told it this session — but you didn't have to.

### Tools vs. hooks — the distinction

| | Tool | Hook |
|---|---|---|
| **Who triggers it** | The model, mid-turn | The SDK, on lifecycle events |
| **Model aware of it?** | Yes — it's in the tool list | No — invisible to the model |
| **When it fires** | Whenever the model decides | Fixed events: `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, etc. |
| **Use it for** | Capabilities the agent needs | Guardrails, context injection, audit logging, blocking dangerous ops |

Memory needs both: a **tool** so the agent can *choose* what to remember, and a **hook** so the remembered context gets *automatically* injected.

### Look at the code

Open [`memory.py`](./memory.py). The tool half looks familiar — `@tool` decorator, MCP server. The hook half is the new shape: an async function with a specific signature, wrapped in `HookMatcher`.

---

## That's the progressive demo

You just saw one task get progressively better by layering on SDK primitives — each one adding a distinct capability, none of them requiring you to write an agentic loop.

**The lesson is in `agent.py:build_options()`.** Open it. Read it top to bottom. Every toggle in `config.py` maps to one block in that function, and each block sets exactly one SDK option. That's the whole API surface you need for production agents.

**Want to see exactly what the model sees?** Run `./workshop demo --show-prompt`. It dumps the full assembled system context — prompt, allowed tools, sub-agent definitions, hooks — everything the SDK built from your config. Run it at each stage and watch the context grow.

During the break, try:
- Asking for a comparison briefing (Tinplate vs. Bucklefern)
- Telling the agent an unusual preference and seeing if it sticks
- Swapping `MODEL` to `"claude-opus-4-6"` and re-running
- `./workshop reset` then re-running to watch the agent forget

Then head to [`../02-breakouts/`](../02-breakouts/).
