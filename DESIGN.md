# Design Notes

Context for people maintaining or extending this workshop repo. If you're *attending* the workshop, you don't need to read this — start with `./workshop check` and the [README](./README.md).

---

## What this repo is for

Hands-on workshop materials for the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python). Two parts:

1. **Guided demo** (`01-guided-demo/`) — A single agent with three boolean toggles. Attendees flip one switch at a time and re-run, watching the same task get progressively more capable. Teaches the SDK primitives by showing, not telling.

2. **Breakouts** (`02-breakouts/`) — Pre-built tool and sub-agent libraries that attendees assemble into agents for their chosen use case. Teaches composition and prompt engineering.

Target audience is technical leaders (VP/Director level) who are familiar with LLMs and comfortable in a terminal but may not have written production code recently. Both sessions are designed so **attendees never write code** — they flip switches, pick from lists, and write prompts.

---

## Design principles

### Progressive, not disconnected

The guided demo uses **one cohesive task** (company briefing) across all four stages. You ask the same question at each stage and watch the answer get better. This is more visceral than four unrelated toy demos — attendees *feel* each capability land.

### No building, only assembling

Every capability is pre-built. Attendees make decisions (which toggle, which tool category, what prompt) but never write `@tool` decorators or `AgentDefinition` objects themselves during the session. They *read* those in the source, but the active loop is flip→run→observe, not write→debug.

### Local mock data only

Every tool is backed by static JSON in the repo. No external APIs, no third-party keys, no network dependencies beyond the Claude API itself. This eliminates the #1 cause of workshop derailment ("half the room is still setting up their Salesforce credentials").

In production you'd swap the mock implementations for real integrations — the `@tool` contract stays the same. The workshop teaches the pattern; the data is scaffolding.

### Under 2 minutes to first output

Clone → `pip install` → `cp .env.example .env` + paste key → `./workshop demo` → see output. The `./workshop check` script exists to catch setup issues (wrong Python version, missing key, edited `.env.example` instead of `.env`) *before* the timed exercises begin.

### Symmetrical structure

All breakouts have the same shape (`config.py` + `run.py` + `README.md` + `data/`) and use the same `_shared/` runner. Learn one, you can facilitate any room.

---

## Key pedagogical moments

### `build_options()` is the lesson

`01-guided-demo/agent.py:build_options()` is the teaching centerpiece. It has four blocks — one per toggle — and each block shows exactly which `ClaudeAgentOptions` field gets populated when that capability is enabled.

The explicit goal: an attendee reads that function top to bottom and walks away knowing the full API surface. Everything else in the repo supports getting them to that moment.

### The comparison tables

Two distinctions confuse people new to the SDK:

1. **Main agent vs. sub-agent** — "Who defines it, who invokes it, whose context window" table in GUIDE.md Stage 2
2. **Tool vs. hook** — "Who triggers it, is the model aware, what's it for" table in GUIDE.md Stage 3

These tables appear in the guide, in the FAQ, and in CHEATSHEET.md. Repetition is intentional.

### The edge-case scenarios

Several breakouts have a deliberately tricky case that rewards careful prompting:

- **customer-support / T-1050:** Customer says "duplicate charge, refund me." Account is past-due, so the two charges are legitimate (catch-up + current). Lazy prompt → bad refund. Verify-before-acting prompt → correct explanation.
- **account-intelligence / A-2201:** Account looks healthy on usage metrics but their executive sponsor just left. The churn-signals KB flags this. Lazy prompt → "easy renewal." Thorough prompt → "find a new champion first."
- **sre-agent / checkout incident:** Deploy at 11:42 → error spike at 12:03 → runbook RB-001 covers it. The path is solvable; the question is whether the prompt gets the agent to *commit* to it or hedge.

These exist because "make the agent give *an* answer" is trivial — the interesting work is "make the agent give the *right* answer when the obvious move is wrong."

---

## Why the guided demo and breakouts share code patterns but not code

`01-guided-demo/agent.py:build_options()` and `02-breakouts/_shared/agent_base.py:_build_options()` are intentionally the same pattern implemented twice.

The guided demo's version is *readable* — minimal abstraction, every toggle inline, comments everywhere. It's meant to be read.

The breakouts' version is *generalizable* — takes any config module, validates it, translates categories to tool names. It's meant to be used.

If we unified them, either the teaching version would get cluttered with generality, or the breakout version would get cluttered with workshop-specific comments. Two implementations of one pattern is the right trade-off for a teaching repo.

---

## Adding a new breakout

1. Copy `extend/_template/` to `02-breakouts/your-name/`
2. Write mock data JSON matching the shapes in `freeform/data/README.md`
3. Fill in `config.py` with a starting `TOOL_CATEGORIES`, `SUBAGENTS`, and `SYSTEM_PROMPT`
4. Design an edge case — a scenario where the obvious move is wrong
5. Write the README with scenario, test prompts, and "what to tinker with"
6. Add to the table in `02-breakouts/README.md`

See `extend/add-a-breakout.md` for the detailed walkthrough.

---

## Adding a new tool category

Edit `02-breakouts/_shared/tool_library.py`:

1. Define `@tool`-decorated async functions
2. Bundle them: `my_server = create_sdk_mcp_server(name="...", tools=[...])`
3. Add to `TOOL_CATALOG` dict at the bottom

See `extend/add-a-tool.md` for the detailed walkthrough.

---

## Repo hygiene

- All companies, people, and services in mock data are **fictional**
- No external API keys beyond `ANTHROPIC_API_KEY`
- `.gitignore` covers `.env`, `memory_store.json`, `__pycache__/`
- Every tool category's data files are optional — missing files return empty results gracefully, they don't crash
