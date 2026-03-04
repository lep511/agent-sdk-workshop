# Get Structured JSON Output

The breakout agents return prose — great for humans reading a terminal, less great for piping into a downstream system. Here's how to make the agent return validated JSON matching a schema you define.

---

## The concept

The SDK supports **structured outputs**: instead of free text, the model returns JSON that's validated against your schema. If the model's output doesn't match, the SDK tells it to retry — you never see malformed JSON.

This is how you go from "cool demo" to "I can plug this into my pipeline."

---

## Define your schema

Use a standard Python dataclass or TypedDict. For the account-intelligence breakout, a briefing might look like:

```python
from dataclasses import dataclass, field

@dataclass
class AccountBriefing:
    account_id: str
    health: str              # "healthy" | "at-risk" | "upsell-opportunity"
    confidence: str          # "high" | "medium" | "low"
    positive_signals: list[str] = field(default_factory=list)
    risk_signals: list[str] = field(default_factory=list)
    recommended_play: str = ""
```

---

## Wire it into the agent

In your breakout's `config.py`, you'd add the schema to a new field, and `agent_base.py` would pass it to `ClaudeAgentOptions`. Conceptually:

```python
# In config.py
OUTPUT_SCHEMA = AccountBriefing

# In agent_base.py (you'd add this block)
output_schema = getattr(config, "OUTPUT_SCHEMA", None)
if output_schema:
    # SDK API for structured output — check current docs for exact param name
    options_kwargs["output_schema"] = output_schema
```

The exact SDK parameter name may vary by version — check the [Python SDK reference](https://platform.claude.com/docs/en/agent-sdk/python) for `ClaudeAgentOptions` and search for "structured" or "schema".

---

## What changes

**Before (prose):**
```
HEALTH: At-risk (despite strong usage)
SIGNALS:
  ✓ Usage up 40% QoQ
  ⚠ Executive sponsor is leaving
...
```

**After (JSON, validated):**
```json
{
  "account_id": "A-2201",
  "health": "at-risk",
  "confidence": "high",
  "positive_signals": ["Usage up 40% QoQ", "88% seat utilization"],
  "risk_signals": ["Executive sponsor departure (Feb 4)"],
  "recommended_play": "Identify new champion before renewal. Move conversation earlier."
}
```

Now you can `json.loads()` the output and feed it straight into Salesforce, a dashboard, an alert system — whatever.

---

## Trade-offs

- **Prose is better for human review.** A 200-word briefing with nuance doesn't compress into five fields.
- **JSON is better for automation.** If the output feeds a pipeline, you want structure.

Many production agents support both: a `--format json` flag or a separate "export" sub-agent that converts the prose briefing into the structured shape.

---

## Try it

1. Pick a breakout where structured output makes sense (account-intelligence is a natural fit — CRM integration)
2. Define a dataclass for the output shape
3. Wire it into `_build_options()` in `agent_base.py`
4. Re-run and see the difference

The prompt doesn't need to change — the SDK handles schema adherence automatically. But you can tune it: "Keep each signal under 10 words" if you want terse list entries.
