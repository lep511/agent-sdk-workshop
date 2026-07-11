# 02 — Breakouts

**Pick a use case. Build an agent.**

Where the guided demo was a tour (flip a switch, watch what happens), the breakouts are Lego assembly. You get a box of pre-built components — tools, sub-agents — and you decide which to combine and how to instruct the result.

No code writing. Lots of prompt writing. Fast iteration.

---

## Prerequisites

This project uses [UV](https://docs.astral.sh/uv/) for dependency management. Install it if you haven't:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Setup

From the `02-breakouts/` directory:

```bash
# Create virtual environment and install dependencies
uv sync
```

Or let UV handle everything automatically — `uv run` will create the environment and install dependencies on first use.

---

## Pick a breakout

| Breakout | Use case | Good if you work on... |
|---|---|---|
| [**`00-warmup/`**](./00-warmup/) | Same briefing task from the demo — feel the transition | *(start here if new to breakouts)* |
| [**`chief-of-staff/`**](./chief-of-staff/) | Meeting prep, email drafting, exec briefings | Workflow automation, productivity, internal tools |
| [**`customer-support/`**](./customer-support/) | Ticket triage, KB-grounded responses, escalation judgment | Support, CX, customer-facing products |
| [**`sre-agent/`**](./sre-agent/) | Incident investigation, runbook execution, deploy correlation | Observability, infra, platform reliability |
| [**`account-intelligence/`**](./account-intelligence/) | Pre-renewal account review, churn risk detection | Sales ops, revenue, account management |
| [**`freeform/`**](./freeform/) | Blank canvas with the full component library | You have your own use case in mind |

---

## How it works

Every breakout has the same shape:

```
{breakout}/
├── config.py    ← YOU EDIT THIS. Component picks + system prompt.
├── run.py       ← Entry point. Don't touch.
├── README.md    ← Scenario, test prompts, what to try
└── data/        ← Mock JSON the tools read from
```

And every breakout uses the same shared framework in [`_shared/`](./_shared/).

**You edit `config.py`. You run the agent. That's the loop.**

```bash
# From inside any breakout directory:
uv run run.py

# Or from the repo root:
./workshop breakout <name>
```

---

## What's in the toolbox

→ **See [`COMPONENTS.md`](./COMPONENTS.md) for the full reference** — every tool category, every sub-agent, what each needs.

Quick summary:

| | Options |
|---|---|
| **Tool categories** | `schedule` · `knowledge` · `support` · `ops` · `code` · `memory` |
| **Sub-agents** | `researcher` · `summarizer` · `classifier` · `verifier` · `writer` · `procedure_runner` |

---

## The iteration cycle

1. **Read your breakout's README** — understand the scenario and the mock data
2. **Run with the starting config** — see the baseline
3. **Change one thing in `config.py`** — add a sub-agent, tweak the prompt, remove a tool category
4. **Re-run** — did it get better or worse?
5. **Repeat** — most of your time should be on steps 3–4

Component selection usually stabilizes in the first 10 minutes. **Prompt tuning is where the real work is.**

---

## Running without UV

If you prefer not to use UV, you can install dependencies manually:

```bash
pip install claude-agent-sdk>=0.1.41 python-dotenv>=1.0.0
cd <breakout-dir>
python run.py
```

---

## If you finish early

- **Go adversarial:** try to make your agent give a wrong answer. What prompt change would have prevented it?
- **Swap scenarios:** copy another breakout's `data/` into yours — does your prompt still hold up?
- **Extend the library:** see [`../extend/`](../extend/) for recipes on adding your own tools and breakouts
- **Understand the plumbing:** [`_shared/agent_base.py:_build_options()`](./_shared/agent_base.py) translates your config into SDK options. It's the same pattern as `01-guided-demo/agent.py:build_options()`. Compare them.
