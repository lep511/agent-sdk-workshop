# A-2201 — Gold Output Reference

The edge case in this breakout. An account looks healthy on every usage metric but their executive sponsor just left. The churn-signals playbook says this is the #1 leading indicator. Does the agent surface it?

This file shows what a **surface-level prompt** produces vs. what a **dig-deeper prompt** produces.

---

## The account

**Pelledryn Data Sciences (A-2201)** — Growth plan, $3,200 MRR, renewal April 5 (30 days out).

**Surface signals (from `customers.json`):**
- Usage up 40% QoQ
- 22 of 25 seats active
- Positive December QBR — "essential to their workflow"
- Zero open support tickets

**Buried signal (from `tickets.json`, interaction INT-0917):**
- Feb 4: Day-to-day owner emails: "David Oyelaran announced yesterday that he's leaving Pelledryn Data at the end of the month. He's been our exec sponsor for the platform since we brought it in."

**The playbook (`kb-churn-signals`):**
- Lists "executive sponsor departure" as the **#1 leading indicator** of churn, regardless of usage metrics
- "Usage is a lagging indicator. Sponsor departure is a leading one."
- "Action: Immediately identify and cultivate a new champion before the renewal conversation. Do NOT wait for usage to decline."

---

## With a surface-level prompt

**Prompt:** `"You are an account intelligence assistant. When asked about an account, summarize its health and recommend next steps."`

**Typical output:**

> **HEALTH: Strong**
>
> Pelledryn Data Sciences is a healthy account heading into renewal:
> - Usage up 40% quarter-over-quarter
> - High seat utilization (22/25 active)
> - December QBR was very positive — they called the platform "essential"
> - No open support issues
>
> **RECOMMENDED PLAY:** Standard renewal. This should be a smooth close. Consider bundling an expansion conversation given the strong usage trend.

**Why this is wrong:** The agent summarized the account record but never checked interaction history or the playbooks. It missed the sponsor departure entirely. This is a dashboard readout, not intelligence.

---

## With a dig-deeper prompt

**Prompt:** The starting `SYSTEM_PROMPT` in `config.py`, which includes:
- "Review interaction history — support tickets, QBR notes, recent touchpoints"
- "Check the sales playbooks for relevant signals — churn risks, upsell triggers"
- "Don't just summarize the data — interpret it."

**Typical output:**

> **HEALTH: At-risk (despite strong usage)**
>
> **SIGNALS:**
> - ✓ Usage up 40% QoQ, 88% seat utilization — product is sticky
> - ✓ December QBR was positive, team considers platform "essential"
> - ⚠ **Executive sponsor David Oyelaran is leaving at end of month** (per Feb 4 note from Sarah Vance). Replacement not yet named.
>
> **RISKS:**
> The churn-signals playbook flags executive sponsor departure as the #1 leading indicator — it predicts churn *before* usage declines. Strong current usage doesn't protect us if the new VP evaluates tools with fresh eyes and we have no internal champion.
>
> **RECOMMENDED PLAY:**
> 1. **Do NOT treat as standard renewal.** This is a champion-transition situation.
> 2. Get an intro to David's replacement as soon as they're named — have the value story ready (usage data, December QBR feedback, "essential" quote).
> 3. Deepen relationship with Sarah Vance (day-to-day owner) — she's our best remaining advocate.
> 4. Move the renewal conversation *earlier* if possible, while David is still there to give a warm handoff.

**Why this is right:** Looked at interaction history → found the sponsor departure note → cross-referenced the churn-signals playbook → weighed the leading indicator against the lagging one → recommended a specific recovery play.

---

## What made the difference

| Prompt element | Effect |
|---|---|
| "Review interaction history" | Agent calls `get_ticket` / `list_open_tickets` and finds INT-0917 |
| "Check the sales playbooks" | Agent searches KB and finds `kb-churn-signals` |
| "Don't just summarize — interpret" | Agent weighs the sponsor signal against the usage signal instead of listing both neutrally |

The surface-level prompt says "summarize health" — so it summarizes. The dig-deeper prompt says "check the playbooks" — so it finds the rule that says sponsor departure trumps usage metrics.

---

## Validation checklist

Run `./workshop breakout account-intelligence` and try:

- [ ] Default task (A-2201) with starting prompt — should flag the sponsor risk
- [ ] A-2201 with prompt stripped to "summarize the account" — should demonstrate the miss
- [ ] A-3340 (Azurite Clinical Networks) — obvious at-risk case, should be easy
- [ ] A-1908 (Glasswick Content Works) — should identify the expansion opportunity from INT-0876
- [ ] "Review all four accounts, which needs attention first?" — should rank A-2201 as highest priority *despite* its strong metrics
