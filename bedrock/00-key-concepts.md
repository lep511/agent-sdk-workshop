## Accelerate Agentic AI with Claude in AWS

Before you build anything, here's what you need to know about three things: what an AI agent is, what the Claude Agent SDK gives you, and what Amazon Bedrock AgentCore handles in production.

**Time:** ~10 minutes (read-through)

## What is an AI agent?

A chatbot answers a question. An **agent** does the work.

The difference is action. A plain language model takes text in and produces text out. An agent is a language model placed **in a loop, with tools** — so instead of only describing what to do, it can actually go and do it: read a file, run a command, call an API, check the result, and try again.

Every capable agent runs the same fundamental loop:

![Agent Loop](https://static.us-east-1.prod.workshops.aws/d769e1f4-6424-4ddb-93ee-7391eac3ca57/static/images/module-4/claude_agent_sdk_loop.png?Key-Pair-Id=K36Q2WVO3JP7QD&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9zdGF0aWMudXMtZWFzdC0xLnByb2Qud29ya3Nob3BzLmF3cy9kNzY5ZTFmNC02NDI0LTRkZGItOTNlZS03MzkxZWFjM2NhNTcvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc4NDI4NjYxMn19fV19&Signature=M2-4BS0T7jCI-bV-1XoeoIbDYMbiMv5%7E4GiMhhPvI1Chxx%7EfCSxGF9exEoZYWoEAofQZU1NRnOe2UOTkDj3ZjH6R71wGjFe6pz2Y2zk-ikns6HFFOlRId6jX2HHW%7EVuMj6WQKYZO5rJXQrRX3Du0yzJTYzLrgnxrUnbJOn7Viu4OIIX5snOD1Y12Y3-dhstECajrlvzWJvxjJUBzC1yn3lielMqz-XvDc3VB35Dk1jAf%7E7adqsMo%7EC3BUtFmFS2hlcB%7E5wDk0pDpoIqlKVtMwjK6r80zYf2CXhesHDCuRMsyzDk7bt6774khoVcHR7IIOlxnKSa6T6n6TPhbloZQ4g__)

Agent Loop

1. **Gather context** — pull in what's needed: read files, search, inspect data, or recall earlier steps.
2. **Take action** — use tools to change the world or fetch new information: run a command, write a file, query a database.
3. **Verify work** — check whether the action worked. If not, loop back and try again.

This gather-act-verify loop is the heartbeat of an agent. Throughout this workshop, watch for these three steps in what your agent does.

## What is the Claude Agent SDK?

The [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) is a library for building autonomous AI agents. It gives you the **same agent loop, tools, and context management that power Claude Code** — so you can build agents that work the way Claude Code does.

![Claude Agent SDK Architecture](https://static.us-east-1.prod.workshops.aws/d769e1f4-6424-4ddb-93ee-7391eac3ca57/static/images/module-4/claude_agent_sdk_architecture.png?Key-Pair-Id=K36Q2WVO3JP7QD&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9zdGF0aWMudXMtZWFzdC0xLnByb2Qud29ya3Nob3BzLmF3cy9kNzY5ZTFmNC02NDI0LTRkZGItOTNlZS03MzkxZWFjM2NhNTcvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc4NDI4NjYxMn19fV19&Signature=M2-4BS0T7jCI-bV-1XoeoIbDYMbiMv5%7E4GiMhhPvI1Chxx%7EfCSxGF9exEoZYWoEAofQZU1NRnOe2UOTkDj3ZjH6R71wGjFe6pz2Y2zk-ikns6HFFOlRId6jX2HHW%7EVuMj6WQKYZO5rJXQrRX3Du0yzJTYzLrgnxrUnbJOn7Viu4OIIX5snOD1Y12Y3-dhstECajrlvzWJvxjJUBzC1yn3lielMqz-XvDc3VB35Dk1jAf%7E7adqsMo%7EC3BUtFmFS2hlcB%7E5wDk0pDpoIqlKVtMwjK6r80zYf2CXhesHDCuRMsyzDk7bt6774khoVcHR7IIOlxnKSa6T6n6TPhbloZQ4g__)

Claude Agent SDK Architecture

**Claude Code is an agent for coding. The Claude Agent SDK lets you build an agent for anything** — research, data analysis, customer support, operations — on the same proven runtime.

The SDK handles the hard parts for you: the reasoning loop, tool invocation, and context management. You focus on what the agent should do, not the plumbing. There are two ways to run an agent:

| API | Shape | Use it for |
| --- | --- | --- |
| **`query()`** | One function call, stateless | The simplest agent — ask once, get an answer |
| **`ClaudeSDKClient`** | A persistent client, multi-turn | Real applications — keep context across turns, shape behavior with a system prompt, load skills |

Key features you'll use in this workshop:

- **Skills** — progressive, on-demand domain expertise loaded only when relevant
- **`CLAUDE.md`** — project-wide context and guidelines the agent always has in view
- **Bash + scripts** — let the agent run calculations and commands
- **Subagents** — delegate isolated tasks to specialized agents
- **Sessions** — maintain context across exchanges (resume, fork, multi-turn)

## What is Amazon Bedrock AgentCore?

You can build a capable agent on your laptop in an afternoon. **Getting it to production is the hard part.** Session management, security controls, scaling, isolation between users, memory, and observability — teams routinely spend months building this infrastructure.

[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) removes that undifferentiated heavy lifting. It lets you deploy and operate agents securely at scale.

![Bedrock AgentCore](https://static.us-east-1.prod.workshops.aws/d769e1f4-6424-4ddb-93ee-7391eac3ca57/static/images/module-4/bedrock_agent_core.png?Key-Pair-Id=K36Q2WVO3JP7QD&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9zdGF0aWMudXMtZWFzdC0xLnByb2Qud29ya3Nob3BzLmF3cy9kNzY5ZTFmNC02NDI0LTRkZGItOTNlZS03MzkxZWFjM2NhNTcvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc4NDI4NjYxMn19fV19&Signature=M2-4BS0T7jCI-bV-1XoeoIbDYMbiMv5%7E4GiMhhPvI1Chxx%7EfCSxGF9exEoZYWoEAofQZU1NRnOe2UOTkDj3ZjH6R71wGjFe6pz2Y2zk-ikns6HFFOlRId6jX2HHW%7EVuMj6WQKYZO5rJXQrRX3Du0yzJTYzLrgnxrUnbJOn7Viu4OIIX5snOD1Y12Y3-dhstECajrlvzWJvxjJUBzC1yn3lielMqz-XvDc3VB35Dk1jAf%7E7adqsMo%7EC3BUtFmFS2hlcB%7E5wDk0pDpoIqlKVtMwjK6r80zYf2CXhesHDCuRMsyzDk7bt6774khoVcHR7IIOlxnKSa6T6n6TPhbloZQ4g__)

Bedrock AgentCore

AgentCore is **framework- and model-agnostic** — it works with the Claude Agent SDK (what we use here), Strands Agents, LangGraph, CrewAI, and others.

Think of the division of labor as:

- **Claude Agent SDK** = how your agent thinks and acts (the agent loop, tools, skills, context)
- **AgentCore** = how your agent runs in production (deployment, memory, observability, security)

This workshop focuses on three AgentCore components:

| Component | What it does | Where in this workshop |
| --- | --- | --- |
| **Runtime** | Secure, serverless runtime to deploy and scale agents | Lab 2 — deploy your agent |
| **Memory** | Managed short- and long-term memory across sessions | Lab 3 — give your agent memory |
| **Observability** | Trace, debug, and monitor agents via OpenTelemetry | Lab 4 — see what your agent does |

## What you'll learn

| Concept | What you'll master |
| --- | --- |
| **The Agent Loop** | How Claude gathers context, takes action, and verifies results |
| **Context Engineering** | Use skills and `CLAUDE.md` to give your agent domain expertise |
| **Production Deployment** | Deploy to AgentCore Runtime with isolated execution and automatic scaling |
| **Memory** | Add cross-session memory so your agent remembers users between invocations |
| **Observability** | Trace every agent decision in CloudWatch using OpenTelemetry |

## Architecture overview

As you climb the ladder, your agent's architecture grows:

```
Lab 1     Your laptop → Claude Agent SDK
              │
Lab 2     AgentCore Runtime → Your agent (stateless, deployed)
              │
Lab 3     AgentCore Runtime + Memory → Remembers across calls
              │
Lab 4     + CloudWatch / OpenTelemetry → Traced & debuggable
```

Continue to the next page to start building.
