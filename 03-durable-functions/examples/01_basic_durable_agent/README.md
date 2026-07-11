# Example 1: Basic Durable Agent

The simplest Claude Agent SDK + durable functions integration. A research agent that searches and summarizes, with every step checkpointed.

## What it demonstrates

- Wrapping the Claude agent loop in `@durable_execution`
- Each model invocation → a named durable step
- Each tool execution → a named durable step
- Automatic replay on failure (no repeated model calls)

## How it works

```
User prompt
    ↓
step("invoke-model-0") → Claude decides to search
    ↓ checkpoint
step("exec-tool-search_web-1") → search executes
    ↓ checkpoint
step("invoke-model-2") → Claude reads the results, decides to read a doc
    ↓ checkpoint
step("exec-tool-read_document-3") → document fetched
    ↓ checkpoint
step("invoke-model-4") → Claude synthesizes final answer
    ↓
return result
```

If the function crashes after step 1, it replays steps 0 and 1 from the checkpoint (returning cached results) and continues from step 2.

## Run locally (tests)

```bash
cd 03-durable-functions/
uv run pytest tests/test_basic_agent.py -v
```

## Deploy

```bash
cd infrastructure/
sam build && sam deploy --guided
```

## Try these prompts

```json
{"prompt": "What are the key features of AWS Lambda durable functions?"}
{"prompt": "Compare AWS Step Functions with Lambda durable functions"}
{"prompt": "How does the replay model work in durable execution?"}
```

## What to tinker with

- Change `max_turns` to see what happens when the agent loops too long
- Add a new tool (calculator, database lookup) and give it a `_claude_tool_schema`
- Modify the system prompt to change the agent's behavior
- Add retry configuration to the tool execution steps
