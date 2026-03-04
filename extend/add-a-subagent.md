# Add a Sub-agent to the Shared Library

You want a specialist that's not in the existing six. Here's how to add one.

---

## 1. Open the library

`02-breakouts/_shared/subagent_library.py`

The whole library is a single dict: `SUBAGENT_CATALOG`. Each entry is an `AgentDefinition`.

---

## 2. Write your sub-agent

Add an entry to `SUBAGENT_CATALOG`:

```python
SUBAGENT_CATALOG: dict[str, AgentDefinition] = {
    ...
    "translator": AgentDefinition(
        description=(
            "Translates text between languages. Use when you need to "
            "present content in a different language than the source."
        ),
        prompt=(
            "You are a professional translator. You will receive text "
            "and a target language. Produce an accurate, natural-sounding "
            "translation. Preserve tone and register. If a term doesn't "
            "translate cleanly, use the closest equivalent and note it "
            "in brackets."
        ),
        tools=[],  # translator works from the prompt, no tools needed
        model="haiku",
    ),
}
```

**Key fields:**
- `description` — tells the *main agent* when to delegate here. Write it from the orchestrator's perspective.
- `prompt` — the sub-agent's system prompt. Write it from the *sub-agent's* perspective ("you are a...").
- `tools` — list of `mcp__category__tool` names this sub-agent can use. Use the `_tools_for(...)` helper if you want whole categories.
- `model` — usually `"haiku"` for sub-agents (fast, cheap). Only bump to sonnet/opus if the sub-agent needs heavy reasoning.

---

## 3. Declare tool dependencies (optional)

If your sub-agent needs certain tool categories to be useful, add to `SUBAGENT_REQUIRES`:

```python
SUBAGENT_REQUIRES: dict[str, list[str]] = {
    ...
    "translator": [],  # no tool deps — works from prompt alone
}
```

If you list categories here and someone enables your sub-agent without those categories, the runner prints a warning (non-fatal, just a heads-up).

---

## 4. Use it

In any breakout's `config.py`:

```python
SUBAGENTS = ["researcher", "translator"]
```

Re-run. The main agent now has a "translator" option when it calls the `Task` tool.

---

## Design tip

Sub-agents work best with **focused, single-responsibility** roles. "Researcher" and "fact-checker" are good. "Assistant that does everything" is bad — that's just another main agent.

Ask yourself: what would you delegate to a specialist *employee* vs. doing yourself? That's the sub-agent boundary.
