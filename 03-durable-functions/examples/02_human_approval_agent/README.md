# Example 2: Human Approval Agent

An agent that generates a plan and **pauses** until a human approves — demonstrating `waitForCallback` with zero compute cost during the wait.

## What it demonstrates

- The plan → approve → execute pattern
- `waitForCallback` suspending Lambda (no charges while waiting)
- External callback via AWS CLI to resume execution
- Separating "thinking" from "doing" for safety

## The flow

```
┌──────────────────────────────────────────────────────────────┐
│ Phase 1: Planning (compute active)                           │
│                                                              │
│   step("generate-plan") → Claude produces numbered plan      │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ Phase 2: Waiting (ZERO compute cost)                         │
│                                                              │
│   waitForCallback("wait-for-human-approval")                 │
│   → Lambda is suspended                                      │
│   → notify_callback sends plan to Slack/email/dashboard      │
│   → Human reviews...                                         │
│   → Human sends callback (approve or reject)                 │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ Phase 3: Execution (compute active, only if approved)        │
│                                                              │
│   step("invoke-model-0") → Claude executes the plan          │
│   step("exec-tool-send_email-1") → email sent                │
│   step("exec-tool-update_database-2") → record updated       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Why this matters

Production agents that take real-world actions (sending emails, modifying records, deploying code) need a human gate. Without durable functions, you'd need:

- A separate API + database to store pending approvals
- A polling mechanism or webhook receiver
- State machine logic to resume the workflow

With durable functions, it's one `waitForCallback` call.

## Try these prompts

```json
{"prompt": "Send a renewal reminder to customer acme-corp at acme@example.com"}
{"prompt": "Update the pricing tier for customer beta-labs from 'starter' to 'enterprise'"}
{"prompt": "Send a sorry email to upset-customer@example.com about their billing issue"}
```

## Approving/rejecting (after deploy)

```bash
# Approve
aws lambda send-durable-execution-callback-success \
  --callback-id <callback-id-from-output> \
  --result '{"approved": true}'

# Reject with reason
aws lambda send-durable-execution-callback-success \
  --callback-id <callback-id-from-output> \
  --result '{"approved": false, "reason": "Email tone is too casual"}'
```

## What to tinker with

- Change the system prompt to affect how plans are written
- Add more tools (Slack notifications, ticket creation)
- Modify `approval_timeout_hours` — what happens on timeout?
- Change `notify_approver` to integrate with your team's approval workflow
