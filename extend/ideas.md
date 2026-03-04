# Agent Ideas

Stuck on what to build? Here are one-line prompts. Each maps to tool categories you already have.

---

## Works with the existing tool library

| Agent | Job | Tool categories | Sub-agents |
|---|---|---|---|
| **Onboarding buddy** | Help new hires find docs, people, and next steps | `knowledge`, `schedule`, `memory` | `researcher` |
| **Deal desk** | Review contract terms against standard policy, flag deviations | `knowledge`, `support` | `verifier`, `classifier` |
| **QBR prep** | Pull account data + playbook → draft the QBR narrative | `support`, `knowledge`, `memory` | `researcher`, `writer` |
| **Internal help desk** | Employee questions routed against internal docs | `knowledge`, `memory` | `classifier`, `researcher` |
| **Release notes writer** | Read the changelog, write human-readable notes | `code`, `knowledge` | `summarizer`, `writer` |
| **Runbook auditor** | Check runbooks against recent incidents — which ones are stale? | `ops`, `knowledge` | `verifier` |
| **Meeting debrief** | Turn rough meeting notes into action items + follow-up emails | `knowledge`, `schedule` | `summarizer`, `writer` |
| **Escalation router** | Look at a ticket, decide which team/person owns it | `support`, `knowledge` | `classifier` |
| **Postmortem assistant** | Given an incident, draft the postmortem skeleton | `ops`, `knowledge`, `memory` | `researcher`, `writer` |
| **Vendor review** | Evaluate a vendor proposal against internal criteria | `knowledge` | `verifier`, `classifier` |

---

## Needs a new tool (see `add-a-tool.md`)

| Agent | Missing capability |
|---|---|
| **Alerting sentry** | Needs a `send_notification` tool (Slack, PagerDuty) |
| **Data quality monitor** | Needs a `run_query` tool (SQL against your warehouse) |
| **Code reviewer** | Needs `get_pr_diff` (GitHub API) |
| **Spend analyzer** | Needs `get_cloud_costs` (AWS Cost Explorer, GCP Billing) |

---

## The meta-question

The best agent to build is one where:
1. **A human currently does this job** (so you know what good output looks like)
2. **The data exists** (in a doc, a database, an API — something the tools can reach)
3. **There's a judgment call** (not just retrieval — the agent has to weigh evidence and decide something)

If your idea hits all three, build it.
