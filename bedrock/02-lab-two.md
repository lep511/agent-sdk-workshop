## Overview

In Lab 1 your agent ran on your laptop. That's great for building, but it's not something real users can reach. In this lab you take the **exact same agent** and deploy it to **Amazon Bedrock AgentCore Runtime** — a fully managed, serverless runtime for agents.

You'll deploy it **bare**: just the agent, running in production, reachable over HTTP. **No memory, no observability yet.** That's deliberate — by the end of this lab you'll feel a real limitation, and the next two labs each fix one.

You are not rebuilding your agent. You're wrapping the Lab 1 agent in an AgentCore entrypoint and letting the platform run it.

## Learning objectives

By the end of this lab, you will be able to:

- Explain what AgentCore Runtime provides and why it beats rolling your own infrastructure
- Wrap your agent in a thin AgentCore entrypoint that **reuses** your Lab 1 logic
- Deploy the agent with the **`agentcore` CLI** (cloud Container build — no local Docker)
- Invoke your deployed agent over HTTP
- **Recognize the limitation** of a stateless deployment (the hook into Lab 3)

## Why AgentCore Runtime?

Recall the POC-to-production gap from the Key Concepts section. Runtime closes the part of that gap that's about *running* the agent:

| Feature | What it gives you |
| --- | --- |
| **Isolated microVM execution** | Each session runs in a secure, isolated sandbox |
| **Serverless & auto-scaling** | No servers to manage; scales with demand; fast cold starts |
| **Built-in identity & credentials** | Secure, managed access to AWS services |
| **Protocol support** | Invoke over HTTP; supports MCP and agent-to-agent |
| **Extended execution** | Built for long-running agentic workloads |

You get all of this with a single deploy command, instead of building it yourself.

## Prerequisites

- Lab 1 completed (you have a working local agent — `chief_of_staff_agent/agent.py`)
- The **`agentcore` CLI** (the `@aws/agentcore` npm package) — the notebook's Setup cell installs it
- Your account/region **CDK-bootstrapped** (`cdk bootstrap`) so the deploy can provision resources

The container image is built **in the cloud** (CodeBuild), so you don't need Docker installed locally. And AgentCore's CDK **auto-creates** the runtime's execution IAM role (Bedrock invoke + CloudWatch Logs) — there's no role for you to write.

## What this lab does

At a high level, deployment is three conceptual steps:

```
Your agent (Lab 1)
       │
       ▼
1. Wrap it in a thin AgentCore entrypoint
   (a handler that receives a request and streams the agent's response)
       │
       ▼
2. Deploy with the agentcore CLI
   (builds a container in the cloud, pushes to ECR, provisions the runtime via CDK)
       │
       ▼
3. Invoke over HTTP
   (send a request to your live agent and stream back the result)
```

## Step 1 — Wrap your agent in an entrypoint (reuse, don't rewrite)

AgentCore runs your agent through a small **entrypoint**: a handler that takes an incoming request payload, runs your agent, and streams the response back. You don't rebuild the agent — the entrypoint (`agent_agentcore.py`) is *thin* and simply calls the same **`build_agent_options()`** from Lab 1's `agent.py`. That one helper stays the single source of truth, so the local and deployed agents are guaranteed identical.

The Claude Agent SDK ships a ~218 MB native CLI binary. Packaged as a zip, that binary loses its execute permission and the agent fails to start. A **Container build** `pip install` s the SDK fresh inside a Linux/ARM64 image, so it has the right architecture and permissions. AgentCore builds this image **in the cloud** — no local Docker needed.

## Step 2 — Deploy with the agentcore CLI

The deployment is declared in `agentcore/agentcore.json` (set up for you). The `agentcore` CLI does the rest — optionally test locally first, then deploy:

- `agentcore dev` — *(optional)* run the agent in a local container to test the request/response loop
- `agentcore deploy -y` — build the image in the cloud, push to ECR, and provision the runtime (via CDK)
- `agentcore status` — confirm the runtime is ready and see its ARN

The CDK **auto-creates** the execution IAM role along the way — you don't write any IAM.

## Step 3 — Invoke your deployed agent

With the agent live, you send it a request over HTTP (`agentcore invoke`) and stream back its response — the same Chief of Staff you ran locally, using the same `CLAUDE.md` company context and `financial-analysis` skill, now serving from managed infrastructure.

The config ships with `enableOtel` on, so traces are *already* flowing to CloudWatch from your first invocation. You'll explore them in **Lab 4**.

## Hands-on exercise

You can also view the code on [GitHub](https://github.com/aws-samples/sample-agentic-ai-with-claude-agent-sdk-and-amazon-bedrock-agentcore/tree/main/foundations/build-an-ai-chief-of-staff/module-2-deploy) .

1. If you haven't already, open the **Module4CodeEditorURL** from [Event Outputs](https://prod.workshops.aws/event/dashboard/en-US) to launch VS Code with the workshop repository.
2. In your Code Editor, open the notebook at:

```bash
foundations/build-an-ai-chief-of-staff/module-2-deploy/module-2-deploy.ipynb
```

3. See how the entrypoint **reuses** `build_agent_options()` (no duplicated agent logic).
4. *(Optional)* Test locally with `agentcore dev`.
5. Run `agentcore deploy -y`, then `agentcore status`.
6. Run `agentcore invoke` on the deployed agent and confirm it responds.
7. Tear it down with `agentcore remove` when you're done.

## The limitation you'll hit (and why it matters)

Now try this against your deployed agent: **invoke it twice in a row, where the second request depends on the first.**

It won't remember. Each invocation is independent — the agent has no idea who you are or what you asked a moment ago. The in-session memory you saw in Lab 1 lived in a single local process; a deployed, scalable agent starts fresh every time.

That's not a bug — it's what "stateless" means, and it's the right default for an isolated, auto-scaling runtime. But for a real product, users expect to be remembered.

Your agent runs in production, but it forgets you between calls. Next, we give it **memory**.

## Key takeaways

- AgentCore Runtime gives you isolated, auto-scaling, managed execution with a single `agentcore deploy`.
- You deploy your **existing** agent by wrapping it in a thin entrypoint that **reuses `build_agent_options()`** — not by rewriting it.
- The image is a **Container** (Linux/ARM64) built **in the cloud** — no local Docker — and the CDK **auto-creates** the execution IAM role.
- A bare deployment is **stateless**: it forgets you between invocations — which is exactly what Lab 3 fixes.

Continue to the next page to give your agent memory.
