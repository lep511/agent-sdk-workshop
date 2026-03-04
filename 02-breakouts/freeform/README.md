# Freeform — Build Your Own

You have your own use case in mind. Here's a blank canvas with the full component library.

---

## What's different about this breakout

The other breakouts give you a pre-configured starting point (tools selected, prompt written, mock data supplied). This one gives you **nothing pre-selected** — the `config.py` is commented-out stubs and an empty system prompt.

The tradeoff: more freedom, more work. You'll need to:
1. Pick your tool categories and sub-agents
2. Write a system prompt from scratch
3. Either copy mock data from another breakout or write your own

---

## How to run

From the repo root:

```bash
./workshop breakout freeform
```

The runner will warn you that your system prompt is empty — that's your cue to go fill in `config.py`.

---

## Suggested approach

Rather than trying to design everything up front:

1. **Start minimal.** Uncomment one tool category and write a three-sentence prompt. Run it.
2. **Add one thing at a time.** One more tool category, or one sub-agent, or one more paragraph of prompt. Run again.
3. **Iterate on the prompt more than the components.** In most cases the component selection stabilizes quickly and the real work is prompt tuning.

The other breakouts' configs are worth mining for patterns — their system prompts especially.

---

## Ideas if you're stuck

- **Sales ops agent** — `knowledge` + `support` tools, customer research + CRM context
- **HR / people-ops agent** — `knowledge` for policy docs, `schedule` for interview coordination, `memory` for candidate history
- **Compliance review agent** — `knowledge` + `verifier` sub-agent to check documents against policy
- **Release notes writer** — `code` tools to read changelogs, `writer` sub-agent for polish
- **Internal help desk** — a lighter version of customer-support but for employee questions

---

## Data

See [`data/README.md`](./data/README.md) for the JSON file shapes each tool category expects. Fastest path: `cp` the data directory from a breakout that's close to your use case and edit.
