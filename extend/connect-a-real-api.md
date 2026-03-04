# Connect a Real API

The workshop tools are all mock JSON. Here's how to swap one for a real integration.

---

## The contract stays the same

This is the whole point: your `@tool` function has a fixed contract. The model doesn't know or care whether the implementation reads JSON or hits an API. Swap the body, keep the signature.

**Before (mock):**

```python
@tool(
    "search_knowledge_base",
    "Search the internal knowledge base for articles matching a query.",
    {"query": str},
)
async def search_knowledge_base(args: dict) -> dict:
    kb = _load("knowledge_base.json")  # ← static JSON
    query = args.get("query", "").lower()
    matches = [a for a in kb if query in a.get("title", "").lower()]
    return _text_result(f"Found {len(matches)} article(s): ...")
```

**After (real API):**

```python
import httpx

@tool(
    "search_knowledge_base",
    "Search the internal knowledge base for articles matching a query.",
    {"query": str},
)
async def search_knowledge_base(args: dict) -> dict:
    query = args.get("query", "")
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://your-kb.example.com/api/search",
            params={"q": query},
            headers={"Authorization": f"Bearer {os.environ['KB_API_KEY']}"},
        )
        results = resp.json()
    return _text_result(format_results(results))
```

Same name, same description, same schema. The agent's behavior doesn't change — only the data source does.

---

## Practical tips

**Use async HTTP.** `httpx.AsyncClient` (not `requests`). The `@tool` handler is `async def` for a reason — don't block the event loop.

**Handle failures gracefully.** Real APIs time out, rate-limit, return 500s. Return a helpful error in the `text` field rather than raising — the agent can work with "search failed, try again" but crashes on an uncaught exception.

```python
try:
    resp = await client.get(...)
    resp.raise_for_status()
except httpx.HTTPError as e:
    return _text_result(f"Search failed: {e}. Try a different query.")
```

**Keep secrets in `.env`.** Add your new key next to `ANTHROPIC_API_KEY`:

```
ANTHROPIC_API_KEY=sk-ant-...
KB_API_KEY=your-kb-key
```

Then load it with `os.environ["KB_API_KEY"]`. The `load_dotenv()` call in `agent_base.py` picks up everything in `.env`.

**Start narrow.** Swap one tool, verify it works, then expand. Don't rewrite all 19 tools at once.

---

## Which tools to swap first

| Tool | Real integration |
|---|---|
| `search_knowledge_base` | Notion API, Confluence API, internal wiki search |
| `lookup_customer` | Salesforce, HubSpot, your CRM |
| `get_ticket` | Zendesk, Linear, Jira |
| `get_calendar` | Google Calendar API, Microsoft Graph |
| `query_metrics` | Datadog, Grafana, CloudWatch |
| `send_slack_message` *(if you added it)* | Slack Web API |
