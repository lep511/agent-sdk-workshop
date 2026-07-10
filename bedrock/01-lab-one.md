## Overview

This is the first rung of the ladder. You'll build an agent **on your own machine** using the Claude Agent SDK, running on Amazon Bedrock for the model.

The agent you'll build is a **Chief of Staff** for *TechStart Inc* — a fictional 50-person Series A startup. A good chief of staff knows the company cold (burn rate, runway, headcount, priorities) and can crunch the numbers on a decision like "should we hire 5 engineers?" You'll build exactly that, in two steps:

- **1a — The one-liner.** Stand up a working agent in a handful of lines with `query()`. Ask it *"What's our runway?"* — and watch it come up empty, because it knows nothing about your company yet.
- **1b — The real Chief of Staff.** Upgrade to `ClaudeSDKClient` and give it what it needs: a **`CLAUDE.md`** that holds company memory, **Bash + Python scripts** to run financial models, **subagents** to delegate specialized analysis, and **multi-turn** conversation.

This agent runs entirely on local files and scripts — no internet, no database, no third-party services. That keeps Lab 1 about *learning the SDK*, not wiring up infrastructure.

## Learning objectives

By the end of this lab, you will be able to:

- Run an agent with the Claude Agent SDK on Amazon Bedrock
- Explain the difference between **`query()`** (stateless) and **`ClaudeSDKClient`** (stateful, multi-turn)
- Give an agent company memory with **`CLAUDE.md`** and domain expertise with **skills**
- Let an agent **run scripts** via the **Bash** tool
- Delegate specialized work to **subagents** with the **Task** tool
- Hold a **multi-turn** conversation where the agent remembers earlier turns

## Before you start

The local ladder needs almost nothing:

- The workshop repo cloned, with dependencies installed (`uv sync`)
- AWS credentials configured
- **Amazon Bedrock model access** for the Claude model you'll use

That's it — no databases, no buckets, no extra infrastructure. (Heavier setup lives only in the optional Advanced chapter.)

## Lab structure

| Part | What you build | Duration |
| --- | --- | --- |
| **1a: The one-liner** | A minimal agent with `query()` — and the moment it falls short | 15 min |
| **1b: The real Chief of Staff** | `ClaudeSDKClient` + `CLAUDE.md` + scripts + subagents + multi-turn | 25 min |

## Part 1a: The one-liner (query())

The fastest way to see an agent work is the `query()` function. You give it a prompt and a list of allowed tools, and it runs the **gather → act → verify** loop on its own until it has an answer. The notebook points it at the `chief_of_staff_agent/` folder with just `Read` and `Bash` allowed — and it takes only a handful of lines.

**What 1a demonstrates:**

- An agent loop, running, in just a few lines of code
- How the agent decides on its own which tools to call and when
- That `query()` is **stateless** — each call is independent and remembers nothing from the last

This is the "aha, that's all it takes?" moment. It's intentionally minimal so the SDK feels approachable.

But ask this Chief of Staff *"What's our runway?"* and it has nothing to say — it doesn't know TechStart's burn rate, cash, or headcount. A capable-looking agent is useless without **context**. That gap is exactly what Part 1b fills.

1a shows both that `query()` is **stateless** (ask a follow-up and it forgets the last turn) *and* that a context-free agent can't do real work. Part 1b fixes both.

## Part 1b: The real Chief of Staff (ClaudeSDKClient + context)

Now you turn that empty shell into a genuine Chief of Staff. You switch to `ClaudeSDKClient`, which keeps a session open for a real back-and-forth, and — by setting `setting_sources=["project"]` and pointing it at the `chief_of_staff_agent/` folder — you give the agent the context and tools it needs (its `CLAUDE.md`, skills, scripts, and subagents all live on disk).

Now ask *"What's our runway?"* again and it answers immediately — *"~20 months, $500K/month burn, $10M in the bank"* — straight from company memory. Here's what changed:

- **`CLAUDE.md`** — always-on company memory (burn rate, runway, headcount, priorities)
- **Skills** — on-demand domain expertise loaded only when relevant (context engineering)
- **Bash + scripts** — run Python financial models deterministically
- **Subagents** — delegate to specialists like a `financial-analyst`
- **Multi-turn** — `ClaudeSDKClient` keeps the session open for follow-ups

## From 1a to 1b: what actually changed

| Capability | 1a · `query()` | 1b · `ClaudeSDKClient` + context |
| --- | --- | --- |
| "What's our runway?" | "I don't have that information." | "~20 months at $500K/mo burn" — from `CLAUDE.md` |
| Conversation | One-shot, stateless | Multi-turn, remembers within the session |
| Running the numbers | Can't | Runs `hiring_impact.py` and friends via Bash |
| Specialized analysis | One generalist | Delegates to the `financial-analyst` subagent |
| Reliability | Varies run to run | Grounded in company data, repeatable |

## CLAUDE.md — company memory

`CLAUDE.md` is an always-on context file the agent reads at the start of every session. For the Chief of Staff it holds TechStart's reality: burn rate, runway, cash, headcount, key metrics, compensation benchmarks, current priorities.

## Skills — packaged domain expertise

Agent Skills are a lightweight, open format for extending an agent's capabilities. A skill is a folder of organized files — instructions, scripts, assets, resources — that the agent discovers and loads to perform a task accurately. Skills are an **open standard** used across many platforms (Claude Code, Codex, Gemini CLI, and more).

![Agent Skills Structure](https://static.us-east-1.prod.workshops.aws/d769e1f4-6424-4ddb-93ee-7391eac3ca57/static/images/module-4/agent-skills-structure.png?Key-Pair-Id=K36Q2WVO3JP7QD&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9zdGF0aWMudXMtZWFzdC0xLnByb2Qud29ya3Nob3BzLmF3cy9kNzY5ZTFmNC02NDI0LTRkZGItOTNlZS03MzkxZWFjM2NhNTcvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc4NDI4NjYxMn19fV19&Signature=M2-4BS0T7jCI-bV-1XoeoIbDYMbiMv5%7E4GiMhhPvI1Chxx%7EfCSxGF9exEoZYWoEAofQZU1NRnOe2UOTkDj3ZjH6R71wGjFe6pz2Y2zk-ikns6HFFOlRId6jX2HHW%7EVuMj6WQKYZO5rJXQrRX3Du0yzJTYzLrgnxrUnbJOn7Viu4OIIX5snOD1Y12Y3-dhstECajrlvzWJvxjJUBzC1yn3lielMqz-XvDc3VB35Dk1jAf%7E7adqsMo%7EC3BUtFmFS2hlcB%7E5wDk0pDpoIqlKVtMwjK6r80zYf2CXhesHDCuRMsyzDk7bt6774khoVcHR7IIOlxnKSa6T6n6TPhbloZQ4g__)

Agent Skills Structure

Skills load **only what's needed, when it's needed** (progressive disclosure):

| Layer | When loaded |
| --- | --- |
| **Metadata** (name + description) | Always — so the agent knows the skill exists |
| **Instructions** (`SKILL.md` body) | When the skill is triggered |
| **Resources** (reference files, scripts) | Only as needed |

## Bash + scripts

With the **Bash** tool, the agent can run the Python scripts that ship with the project — for example a hiring-impact model. The math stays deterministic and auditable.

## Subagents

The main agent can **delegate** to a **subagent** via the **Task** tool. The Chief of Staff project defines specialists like a `financial-analyst`, each with its own focused instructions.

## Skills vs. Tools vs. MCP vs. Subagents

|  | Skills | Tools | MCP | Subagents |
| --- | --- | --- | --- | --- |
| **Provides** | Procedural knowledge | Low-level capabilities | Tool connectivity to external systems | Task delegation |
| **Loads** | Dynamically, as needed | Always in context | Always connected | When invoked |
| **Best for** | "How *we* do it" | Reading, running, querying | Bringing in external data/tools | Parallel, isolated work |

![Skills vs others](https://static.us-east-1.prod.workshops.aws/d769e1f4-6424-4ddb-93ee-7391eac3ca57/static/images/module-4/skills-vs-others.png?Key-Pair-Id=K36Q2WVO3JP7QD&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9zdGF0aWMudXMtZWFzdC0xLnByb2Qud29ya3Nob3BzLmF3cy9kNzY5ZTFmNC02NDI0LTRkZGItOTNlZS03MzkxZWFjM2NhNTcvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc4NDI4NjYxMn19fV19&Signature=M2-4BS0T7jCI-bV-1XoeoIbDYMbiMv5%7E4GiMhhPvI1Chxx%7EfCSxGF9exEoZYWoEAofQZU1NRnOe2UOTkDj3ZjH6R71wGjFe6pz2Y2zk-ikns6HFFOlRId6jX2HHW%7EVuMj6WQKYZO5rJXQrRX3Du0yzJTYzLrgnxrUnbJOn7Viu4OIIX5snOD1Y12Y3-dhstECajrlvzWJvxjJUBzC1yn3lielMqz-XvDc3VB35Dk1jAf%7E7adqsMo%7EC3BUtFmFS2hlcB%7E5wDk0pDpoIqlKVtMwjK6r80zYf2CXhesHDCuRMsyzDk7bt6774khoVcHR7IIOlxnKSa6T6n6TPhbloZQ4g__)

Skills vs others

The Chief of Staff can also use output styles, plan mode, custom slash commands, and hooks. You'll meet the rest in the notebooks and later labs.

## Hands-on exercise

You can also view the code on [GitHub](https://github.com/aws-samples/sample-agentic-ai-with-claude-agent-sdk-and-amazon-bedrock-agentcore/tree/main/foundations/build-an-ai-chief-of-staff/module-1-local-agent) .

1. If you haven't already, open the **Module4CodeEditorURL** from [Event Outputs](https://prod.workshops.aws/event/dashboard/en-US) to launch VS Code with the workshop repository.
2. In your Code Editor, open the notebook at:

```bash
foundations/build-an-ai-chief-of-staff/module-1-local-agent/module-1-local-agent.ipynb
```

3. **Part 1A** — Run the `query()` one-liner. Watch the agent loop run, then ask *"What's our runway?"* and see it come up empty.
4. **Part 1B** — Upgrade to `ClaudeSDKClient` pointed at the `chief_of_staff_agent/` project (`CLAUDE.md`, skills, `scripts/`, subagents). Ask about runway and a hiring decision, then a follow-up — and watch it remember within the session.
5. **All together** — Run the packaged `agent.py` entrypoint, which wraps that configuration behind a single `build_agent_options()` helper. This is the exact agent **Lab 2 deploys**.

## Key takeaways

- An agent is a model **in a loop with tools** — `query()` shows how little code that takes.
- `query()` is **stateless**; `ClaudeSDKClient` is **stateful and multi-turn**.
- **Context engineering** is what makes an agent genuinely useful: `CLAUDE.md` for always-on company memory, **skills** for on-demand expertise, **Bash + scripts** to run real calculations, and **subagents** to delegate specialized work.
- All of this still runs **on your laptop**. Next, we put it in production.

Continue to the next page to deploy this agent to production.
