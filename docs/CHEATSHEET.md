# Agent SDK Cheat Sheet

One page. Every shape you need. Keep this open while you build.

---

## Define a tool

```python
from claude_agent_sdk import tool

@tool(
    "tool_name",                    # what the model sees
    "When to use this tool...",     # guides the model's decision
    {"arg_name": str, "count": int} # schema — Python types, auto-converted
)
async def my_tool(args: dict) -> dict:
    value = args.get("arg_name", "")
    # ... do work ...
    return {"content": [{"type": "text", "text": "result here"}]}
```

## Bundle tools into an MCP server

```python
from claude_agent_sdk import create_sdk_mcp_server

my_server = create_sdk_mcp_server(
    name="myserver",
    version="1.0.0",
    tools=[my_tool, another_tool],
)
# Tool names become: mcp__<server_key>__<tool_name>
# where server_key is the dict key you use in mcp_servers={...}
```

## Define a sub-agent

```python
from claude_agent_sdk import AgentDefinition

researcher = AgentDefinition(
    description="When the orchestrator should delegate to me",
    prompt="You are a research analyst. Given a question, ...",
    tools=["mcp__myserver__tool_name"],  # this agent's allowlist
    model="haiku",                       # optional override
)
```

## Define a hook

```python
from claude_agent_sdk import HookMatcher
from claude_agent_sdk.types import HookContext, HookInput, HookJSONOutput

async def my_hook(
    input_data: HookInput, tool_use_id: str | None, context: HookContext
) -> HookJSONOutput:
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "Injected into the model's context",
        }
    }

matcher = HookMatcher(matcher=None, hooks=[my_hook])
```

## Wire it all up

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

options = ClaudeAgentOptions(
    model="claude-sonnet-4-6",
    system_prompt="You are ...",
    mcp_servers={"myserver": my_server},
    allowed_tools=["mcp__myserver__tool_name", "Task"],
    agents={"researcher": researcher},
    hooks={"UserPromptSubmit": [matcher]},
    permission_mode="bypassPermissions",
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Do the thing")
    async for message in client.receive_response():
        # handle AssistantMessage, UserMessage, ResultMessage
        ...
```

---

## Hook events

| Event | Fires when | Common use |
|---|---|---|
| `UserPromptSubmit` | User message about to go to model | Inject context, audit logging |
| `PreToolUse` | Before a tool runs | Block dangerous ops, validate inputs |
| `PostToolUse` | After a tool returns | Transform results, side effects |
| `Stop` | Agent turn completes | Cleanup, metrics |

---

## See it in this repo

| Pattern | File |
|---|---|
| Tool definition | `01-guided-demo/tools.py` · `02-breakouts/_shared/tool_library.py` |
| Sub-agent definition | `01-guided-demo/subagents.py` · `02-breakouts/_shared/subagent_library.py` |
| Hook definition | `01-guided-demo/memory.py` |
| Options assembly | `01-guided-demo/agent.py:build_options()` — **read this one first** |
| Message rendering | `01-guided-demo/agent.py:render_message()` |

---

## Key distinctions

**Main agent vs. sub-agent:** Main agent is the one *you* talk to via `client.query()`. Sub-agents are *its* workers, spawned via the `Task` tool, with isolated context.

**Tool vs. hook:** Tools are called by the *model*, mid-turn. Hooks are called by the *SDK*, on lifecycle events. The model knows about tools; hooks are invisible to it.
