# 03 — Durable Functions

**Make your agents survive failures, wait for humans, and run for days.**

Where `01-guided-demo` teaches the agent loop and `02-breakouts` teaches composition, this module teaches **durability** — wrapping your Claude Agent SDK agent inside an AWS Lambda durable function so that every tool call is checkpointed, every failure auto-retries, and the agent can pause for hours (or days) waiting for a human decision without paying for idle compute.

---

## Why durable agents?

A vanilla Lambda + Claude Agent SDK agent works great for simple tasks. But production agents hit harder problems:

| Problem | Durable solution |
|---|---|
| Lambda times out mid-tool-loop | Each step is checkpointed; function resumes where it left off |
| External API is flaky | Steps auto-retry with exponential backoff |
| Agent needs human approval to proceed | `waitForCallback` pauses without compute charges (up to 1 year) |
| Multi-agent pipeline costs $$ if any step fails | Saga pattern with compensating transactions |
| Need to correlate agent runs with observability | Execution IDs + CloudWatch traces |

---

## Prerequisites

- Python 3.13+ (SDK comes pre-installed in Lambda runtime) or 3.11+ (bring your own layer)
- AWS CLI 2.33+ configured (`aws sts get-caller-identity`)
- SAM CLI 1.153+ or CDK v2.237+ for deployment
- Amazon Bedrock model access enabled for Claude in your region (no API key needed)

---

## Structure

```
03-durable-functions/
├── README.md                          ← You are here
├── pyproject.toml                     ← Dependencies for local dev/testing
├── lib/
│   ├── __init__.py
│   └── claude_durable.py             ← Glue: Claude Agent SDK + durable steps
├── examples/
│   ├── 01_basic_durable_agent/       ← Simplest agent with durable steps
│   │   ├── handler.py
│   │   └── README.md
│   ├── 02_human_approval_agent/      ← Agent that waits for human sign-off
│   │   ├── handler.py
│   │   └── README.md
│   └── 03_multi_agent_orchestrator/  ← Parent durable fn spawning sub-agents
│       ├── handler.py
│       └── README.md
├── tests/
│   └── test_basic_agent.py           ← Local tests with DurableFunctionTestRunner
└── infrastructure/
    └── template.yaml                 ← SAM template for deploying
```

---

## Quick start (local testing)

```bash
cd 03-durable-functions/

# Install deps (uses uv like the other modules)
uv sync

# Run tests — exercises the durable handler locally without deploying
uv run pytest tests/ -v
```

---

## The three examples

### Example 1: Basic Durable Agent

The simplest integration — a Claude agent loop where each model invocation and tool execution is a durable step. If Lambda crashes mid-loop, it replays from the last checkpoint.

```python
@durable_execution
def handler(event: dict, context: DurableContext) -> dict:
    return run_durable_agent(
        context,
        prompt=event["prompt"],
        system="You are a helpful research assistant.",
        tools=[search_tool, summarize_tool],
    )
```

### Example 2: Human Approval Agent

The agent generates a plan, then **pauses** (zero compute cost) until a human approves via callback. On approval it executes; on rejection it explains why.

### Example 3: Multi-Agent Orchestrator

A parent durable function fans out work to child agents (each its own durable Lambda), waits for all to complete, then synthesizes results.

---

## Key concept: mapping the agent loop to durable steps

The Claude Agent SDK runs an internal loop: prompt → model → tool call → tool result → model → ... The durable wrapper makes each iteration a **step**:

```
┌─────────────────────────────────────────────────────┐
│  Durable Execution                                  │
│                                                     │
│  step("invoke-model-1") → Claude responds + tool    │
│         ↓ checkpoint                                │
│  step("exec-tool-search") → tool result             │
│         ↓ checkpoint                                │
│  step("invoke-model-2") → Claude responds (final)   │
│         ↓ checkpoint                                │
│  return result                                      │
└─────────────────────────────────────────────────────┘
```

If the function crashes after `invoke-model-1`, it replays from that checkpoint — the model call is **not re-executed** (its result was persisted). This is critical because:

1. You don't pay for repeated model invocations
2. The agent doesn't produce different reasoning on retry
3. Tool side-effects don't double-fire

---

## Deploying to AWS

The Claude Agent SDK bundles a ~250MB CLI binary, exceeding Lambda's 250MB zip limit. We deploy as **container images** (supports up to 10GB).

```bash
cd infrastructure/

# One-command deploy (builds image, pushes to ECR, deploys stack)
./deploy.sh
```

Or step by step:

```bash
# 1. Build the container image
cd 03-durable-functions/
docker build --platform linux/arm64 -t durable-agents:latest .

# 2. Push to ECR
aws ecr create-repository --repository-name durable-agents 2>/dev/null
aws ecr get-login-password | docker login --username AWS --password-stdin $ACCOUNT.dkr.ecr.$REGION.amazonaws.com
docker tag durable-agents:latest $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/durable-agents:latest
docker push $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/durable-agents:latest

# 3. Deploy the stack
cd infrastructure/
sam deploy --stack-name sam-app-durable --capabilities CAPABILITY_IAM
```

The SAM template creates:
- Container-based Lambda functions with `DurableConfig`
- IAM role with `AWSLambdaBasicDurableExecutionRolePolicy` + Bedrock access
- Auto-published alias (`live`) for qualified invocation
- Log groups for execution traces

The functions use **Amazon Bedrock** for Claude access — no API key needed, just IAM permissions.

**Invoke with a qualified ARN** (required for durable functions):

```bash
aws lambda invoke \
  --function-name basic-durable-agent:live \
  --payload '{"prompt": "Research the latest AWS announcements"}' \
  --cli-binary-format raw-in-base64-out \
  response.json
```

---

## Iteration cycle

1. Read an example's `README.md` — understand the pattern
2. Run the tests — see the durable replay in action
3. Modify `lib/claude_durable.py` — add retry strategies, change step granularity
4. Add a new tool or change the system prompt
5. Deploy and invoke with real prompts

---

## Further reading

- [AWS Lambda Durable Functions docs](https://docs.aws.amazon.com/lambda/latest/dg/durable-functions.html)
- [Durable Execution Python SDK](https://github.com/aws/aws-durable-execution-sdk-python)
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)
- Workshop module `bedrock/04-lab-four.md` — observability for deployed agents
