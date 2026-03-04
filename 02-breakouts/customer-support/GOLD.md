# T-1050 — Gold Output Reference

The edge case in this breakout. A customer says "duplicate charge, refund me." Their account is past-due, so both charges are legitimate. Does the agent figure this out?

This file shows what a **lazy prompt** produces vs. what a **careful prompt** produces. Use it to calibrate your own results.

---

## The ticket

> **From:** devops@prismwarpmedia.example
> **Subject:** Why was I charged twice?
>
> I see two charges on my card for this month — one on March 1 for $149 and another on March 4 for $149. What's going on? I'm already not happy about the recent price increase and now this. Please refund the duplicate immediately.

Customer C-5560 (Prismwarp Media Works) — Pro plan, $149/mo, account status: **past_due**. Their notes field says "Account went past due last week — payment method expired. Auto-dunning emails sent, no response yet."

---

## With a lazy prompt

**Prompt:** `"You are a helpful customer support agent. Resolve tickets quickly."`

**Typical output:**

> I understand your frustration about the duplicate charges. I've processed a refund of $149 for the duplicate charge on March 4. You should see it back on your card within 5-7 business days. I apologize for the inconvenience.

**Why this is wrong:** The agent never looked up the account. It took the customer's framing ("duplicate") at face value and refunded a legitimate charge. The account is now paid up — and the customer got a free month.

---

## With a careful prompt

**Prompt:** The starting `SYSTEM_PROMPT` in `config.py`, which includes:
- "Look up the customer — their plan tier and history affect what you can offer"
- "Search the knowledge base — most questions have a documented answer"
- "If it requires account changes, refunds, or engineering work, add a note explaining your reasoning"

**Typical output:**

> Hi there — thanks for reaching out, and I understand seeing two charges is frustrating.
>
> I looked into your account and here's what happened: your payment method expired last week, so your March 1 invoice went unpaid. When you updated your card (or when our retry succeeded), the system charged for the overdue March invoice **and** the now-due April invoice. Both charges are valid — one is the catch-up, one is current.
>
> I know that's not the answer you were hoping for. If you'd like, I can walk you through the invoice details so you can see the billing periods covered by each charge. And if there's anything I can do about the recent price change concern, let me know — happy to chat through options.
>
> *(Internal note added: Customer flagged duplicate charge, actually past-due catch-up + current per kb-duplicate-charges. No refund issued. Customer also mentioned price-increase unhappiness — worth a CSM follow-up.)*

**Why this is right:** Looked up the account → noticed past_due status → checked `kb-duplicate-charges` which explicitly covers this case → explained instead of refunding → added an internal note about the underlying sentiment.

---

## What made the difference

| Prompt element | Effect |
|---|---|
| "Look up the customer" | Agent calls `lookup_customer` and sees `status: past_due` |
| "Search the knowledge base" | Agent finds `kb-duplicate-charges` which says "For past-due accounts specifically: the two charges are almost always the catch-up + current. Look at the dates before assuming it's a dupe." |
| "Add a note explaining your reasoning" | Agent records *why* it didn't refund, so a human reviewer can verify |

The lazy prompt has none of these. It just says "be helpful" — which the model interprets as "give the customer what they asked for."

---

## Validation checklist

Run `./workshop breakout customer-support` and try:

- [ ] Default task (T-1047) — should find the KB workaround and either resolve or escalate cleanly
- [ ] T-1050 with starting prompt — should **not** blindly refund
- [ ] T-1050 with prompt changed to just "be helpful, resolve tickets quickly" — should demonstrate the failure mode
- [ ] Add `verifier` sub-agent — does it catch anything the main agent missed?
