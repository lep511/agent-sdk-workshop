# Account Intelligence Agent

Build a pre-renewal briefing agent. Before an AE walks into a renewal call, this agent reviews the account — usage, interaction history, risk signals — and tells them what they're walking into.

The thing that makes this interesting: accounts that **look** healthy on the dashboard can still be in trouble. Good account intelligence surfaces those signals.

---

## The scenario

Four accounts with renewals coming up, each a different archetype:

- **A-2201 (Pelledryn Data Sciences)** — Looks great on paper. Renewal in 30 days. But there's something in the interaction notes worth finding.
- **A-3340 (Azurite Clinical Networks)** — Usage is declining. Three support tickets in the last month. Obvious at-risk signals.
- **A-1908 (Glasswick Content Works)** — Rock-solid, multi-year customer. The question isn't whether they renew — it's what to expand.
- **A-4477 (Wireflint Data Systems)** — New-ish, small contract, quiet. Hard to read. Renew, expand, or not worth the AE's time?

Mock data includes account details, recent interaction history (QBR notes, support touchpoints), and a sales playbook KB covering churn signals, upsell triggers, and competitive displacement.

---

## How to run

```bash
./workshop breakout account-intelligence
```

---

## What to tinker with

### Component selection

- **Add the `verifier` sub-agent** — have it fact-check claims against the interaction history before they go in the briefing. Does it catch anything the main agent got wrong?
- **Remove `knowledge`** — now the agent can't check the playbooks. Does it still spot the risk signal in A-2201, or does it just read the usage numbers back to you?

### The system prompt — the interesting part

The starting prompt says "don't just summarize the data, interpret it." Try tuning:

- **Evidence threshold:** "Flag any risk signal" vs. "only flag risks with multiple confirming data points"
- **Playbook adherence:** "Always check the churn-signals KB before assessing health" — does being explicit help?
- **Output format:** the starting prompt has a HEALTH/SIGNALS/RISKS/PLAY template. Remove it — does the output get muddier?

### Good test prompts

- The default: "Brief me on Pelledryn Data Sciences (A-2201) before Friday's renewal call"
- "Review all four accounts with upcoming renewals. Which needs attention first?"
- "Is Azurite Clinical Networks (A-3340) salvageable or should we expect churn?"
- "What's the upsell play for Glasswick Content Works (A-1908)?"

---

## The edge case to watch

**A-2201 (Pelledryn Data Sciences)** is the judgment test. On the surface: usage up 40% QoQ, zero support tickets, happy QBR in December, renewal in 30 days. Slam dunk?

Check the interaction history. Three weeks ago, their executive sponsor (the person who brought your product in and championed it internally) announced they're leaving. The `kb-churn-signals` playbook lists "executive sponsor departure" as the #1 leading indicator of churn — *regardless* of usage metrics, because usage is a lagging indicator and champion loss is a leading one.

Does your agent:
- Read the happy numbers and say "easy renewal"?
- Find the sponsor-departure note, cross-reference the playbook, and flag it?

The prompt determines which. "Summarize the account" gets you the first. "Check every interaction against the risk playbook before assessing health" gets you the second.

→ See [`GOLD.md`](./GOLD.md) for example outputs showing exactly what the surface-level miss and dig-deeper success look like.
