# Add a New Breakout

You want an agent for a use case that isn't chief-of-staff, customer-support, SRE, or account intelligence. Here's the full process.

---

## 1. Copy the template

```bash
cp -r extend/_template 02-breakouts/my-agent
```

You now have the three files every breakout needs: `config.py`, `run.py`, `README.md`, plus an empty `data/` directory.

---

## 2. Design the scenario

Before writing any config, decide:

- **What's the agent's job?** One sentence. "Triages incoming support tickets." "Prepares account briefings before renewal calls." "Diagnoses production incidents."
- **What data does it need?** What would a human doing this job have open on their screen?
- **What's the interesting judgment call?** Every good breakout has a scenario where the *obvious* move is wrong and a well-prompted agent catches it. This is the thing attendees iterate toward.

Write this down in your README before touching the config.

---

## 3. Create mock data

Drop JSON files in `data/` matching the tool categories you'll use. See `02-breakouts/freeform/data/README.md` for the shapes.

Fastest path: copy data from the breakout closest to yours and edit.

```bash
cp 02-breakouts/customer-support/data/*.json 02-breakouts/my-agent/data/
```

Then tailor the content to your scenario. Make sure the **edge case** is encoded in the data — if "account looks healthy but sponsor left" is your judgment test, the sponsor departure needs to be findable in the interaction history.

---

## 4. Write the starting config

In `config.py`, fill in:

```python
AGENT_NAME = "My Agent"

TOOL_CATEGORIES = [
    "knowledge",  # pick from COMPONENTS.md
]

SUBAGENTS = [
    "researcher",
]

SYSTEM_PROMPT = """You are a ..."""

DEFAULT_TASK = "The test prompt attendees will run first"
```

The starting config should **work** out of the box — it runs, produces plausible output — but be **intentionally imperfect**. Attendees should be able to improve it by adding a sub-agent, adjusting the prompt, etc.

---

## 5. Write the README

Structure:
- One-paragraph description of what the agent does
- **The scenario** — what's in the mock data, what's the setup
- **How to run** — `./workshop breakout my-agent`
- **What to tinker with** — specific things to try (add X sub-agent, tweak the prompt this way)
- **Good test prompts** — 3-5 prompts that exercise different parts of the scenario
- **The edge case to watch** — explain the judgment test, what a lazy agent does vs. a well-prompted one

Look at `customer-support/README.md` or `account-intelligence/README.md` for the voice and depth.

---

## 6. Add to the breakout index

Edit `02-breakouts/README.md` and add a row to the "Pick a breakout" table.

---

## 7. Test it

```bash
./workshop breakout my-agent
```

Run through all your test prompts. Does the starting config work? Can you make it better by following your own "what to tinker with" suggestions?

If you can't improve on the starting config yourself, neither can attendees. Iterate until there's a clear path from "okay output" to "good output."
