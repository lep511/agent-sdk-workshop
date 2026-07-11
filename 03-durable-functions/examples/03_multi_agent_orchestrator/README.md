# Example 3: Multi-Agent Orchestrator

A parent durable function that fans out research to specialized sub-agents, then synthesizes a unified executive briefing.

## What it demonstrates

- Multiple agent runs within one durable execution
- Each sub-agent's work is independently checkpointed
- Coordinator pattern: specialized agents → synthesis agent
- Rate-limit pauses between API calls (via `context.wait`)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Durable Execution: Multi-Agent Orchestrator             │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Sub-agent: Financial Analyst                        │ │
│ │   step("invoke-model-0") → Claude + search_financials│
│ │   step("exec-tool-search_financials-1")             │ │
│ │   step("invoke-model-2") → analysis                 │ │
│ └─────────────────────────────────────────────────────┘ │
│              ↓ checkpoint                               │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Sub-agent: News Analyst                             │ │
│ │   step("invoke-model-3") → Claude + search_news     │ │
│ │   step("exec-tool-search_news-4")                   │ │
│ │   step("invoke-model-5") → analysis                 │ │
│ └─────────────────────────────────────────────────────┘ │
│              ↓ checkpoint                               │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Sub-agent: Competitive Analyst                      │ │
│ │   step("invoke-model-6") → Claude + search_competitors│
│ │   step("exec-tool-search_competitors-7")            │ │
│ │   step("invoke-model-8") → analysis                 │ │
│ └─────────────────────────────────────────────────────┘ │
│              ↓ checkpoint                               │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Synthesis Agent                                     │ │
│ │   step("invoke-model-10") → unified briefing        │ │
│ └─────────────────────────────────────────────────────┘ │
│              ↓                                          │
│ return { briefing, sub_agent_results }                  │
└─────────────────────────────────────────────────────────┘
```

## Why durable orchestration matters

Without durability, if the third sub-agent's model call fails:
- You re-run the entire function
- The first two model calls execute again (costing $$)
- Results might differ (non-deterministic)

With durability:
- Steps 0-8 replay instantly from checkpoint
- Only step 9+ runs live
- Consistent, cost-efficient recovery

## Try these prompts

```json
{"company": "Acme Corp"}
{"company": "CloudTech Industries", "prompt": "Prepare a competitive briefing on {company} for our board meeting."}
{"company": "DataFlow Systems", "prompt": "Assess whether {company} is a viable acquisition target."}
```

## What to tinker with

- Add a fourth sub-agent (e.g., "sentiment_analyst" tracking social media)
- Change the synthesis prompt to produce different output formats
- Add error handling — what if one sub-agent fails? (Saga pattern)
- Make sub-agents run in parallel using `context.map` for true concurrency
- Add a human approval gate between planning and synthesis
