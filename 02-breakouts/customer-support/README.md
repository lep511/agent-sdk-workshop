# Customer Support Agent

Build a tier-1 support agent that triages tickets, searches the knowledge base, and either resolves or escalates — with good judgment about which.

---

## The scenario

Four open tickets in the queue, each a different support archetype:

- **T-1047** — Known issue with a documented workaround. Should be resolvable.
- **T-1048** — Enterprise SSO problem. Probably a common misconfiguration, but there's a churn-risk customer involved.
- **T-1049** — Simple self-serve question. Should take 30 seconds.
- **T-1050** — Angry billing complaint that *looks* like a duplicate charge but might not be.

The mock data includes a knowledge base with documented fixes, customer records with plan tiers and history, and the full ticket threads.

---

## How to run

From the repo root:

```bash
./workshop breakout customer-support
```

---

## What to tinker with

### Component selection

Try adding:
- **`verifier` sub-agent** — before sending a reply, verify the facts match the customer's actual plan/history
- Removing the **`writer` sub-agent** — does reply quality drop when the main agent drafts directly?

### The system prompt — the interesting part

Support agents live or die by their escalation judgment. Try tuning:

- **Escalation threshold:** "Escalate anything involving Enterprise customers" vs. "only escalate if the KB has no answer"
- **Tone calibration:** "Match the customer's energy" vs. "always professional regardless of customer tone"
- **T-1050 specifically:** the billing complaint is a trap — the customer's account is past-due, so the "duplicate" is probably the catch-up charge. Does your prompt give the agent enough judgment to spot this instead of blindly refunding?

### Good test prompts

- "Work through all open tickets in priority order."
- "Triage T-1050. The customer sounds angry — be careful."
- "Is T-1048 something I can fix or does it need engineering?"
- "Draft a reply to T-1049 that's friendly but takes under 10 seconds to read."

---

## The edge case to watch

**T-1050 (Prismwarp Media Works)** is designed to test judgment. The customer says "duplicate charge, refund me." Their account is past-due (payment method expired), so the two charges are almost certainly the overdue payment + current month — both legitimate. The KB article `kb-duplicate-charges` covers exactly this.

Does your agent:
- Blindly refund because the customer is upset?
- Look up the customer, notice the past-due status, and explain the charges?

This is where the prompt matters. "Be helpful" gets you a bad refund. "Verify before acting" gets you the right answer.

→ See [`GOLD.md`](./GOLD.md) for example outputs showing exactly what the lazy-prompt failure and careful-prompt success look like.
