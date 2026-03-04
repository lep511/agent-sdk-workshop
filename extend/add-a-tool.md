# Add a Tool to the Shared Library

You want a capability that's not in the existing 19 tools. Here's how to add one.

---

## 1. Open the library

`02-breakouts/_shared/tool_library.py`

Each tool category is a block: `@tool` functions, then `create_sdk_mcp_server()`, then an entry in `TOOL_CATALOG` at the bottom.

---

## 2. Write your tool function

Find the category that fits (or start a new block). Add a `@tool`-decorated async function:

```python
@tool(
    "send_slack_message",
    "Send a message to a Slack channel. Use for notifications and alerts. "
    "Returns confirmation, does not wait for replies.",
    {"channel": str, "message": str},
)
async def send_slack_message(args: dict) -> dict:
    channel = args.get("channel", "")
    message = args.get("message", "")

    # For the workshop: mock it. In production: call the Slack API here.
    return _text_result(
        f"[MOCK] Would have posted to #{channel}:\n{message}"
    )
```

**Key rules:**
- Must be `async def`
- Must take a single `dict` arg (the SDK passes tool inputs this way)
- Must return `{"content": [{"type": "text", "text": "..."}]}` — use the `_text_result` helper
- The three decorator args are: name, description (guides the model), schema (Python types)

---

## 3. Register it

If adding to an **existing category**, add your function to that category's server and update `TOOL_CATALOG`:

```python
# Add to the server's tools list:
knowledge_server = create_sdk_mcp_server(
    name="knowledge", version="1.0.0",
    tools=[search_knowledge_base, read_document, send_slack_message],  # ← added
)

# Add to the catalog's tool names list:
TOOL_CATALOG = {
    "knowledge": (
        knowledge_server,
        [
            "mcp__knowledge__search_knowledge_base",
            "mcp__knowledge__read_document",
            "mcp__knowledge__send_slack_message",  # ← added
        ],
    ),
    ...
}
```

If adding a **new category**:

```python
notifications_server = create_sdk_mcp_server(
    name="notifications", version="1.0.0",
    tools=[send_slack_message],
)

TOOL_CATALOG = {
    ...
    "notifications": (
        notifications_server,
        ["mcp__notifications__send_slack_message"],
    ),
}
```

The naming convention: `mcp__<category>__<tool_name>`. The `<category>` is the dict key you use in `TOOL_CATALOG`.

---

## 4. Use it

In any breakout's `config.py`:

```python
TOOL_CATEGORIES = ["knowledge", "notifications"]
```

Re-run. Your tool is live.

---

## Reference

The simplest tool in the library is `list_memories` in `tool_library.py` — two lines of logic. The most complex is `query_metrics` — ~30 lines with mock data generation. Your tool will land somewhere between.
