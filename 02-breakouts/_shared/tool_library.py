"""
The tool library — every pre-built tool available to the breakout agents.

You pick which of these to enable via your breakout's config.py.
Each breakout's starting config enables a sensible subset, but you can mix and
match freely.

All tools are backed by local mock data (in ../{breakout}/data/) — no real
APIs, no network calls beyond the Claude API itself. In production you'd swap
the mock implementations for real integrations; the @tool contract stays the
same.

─── Naming convention ────────────────────────────────────────────────────────

Tools are grouped into categories. Each category becomes its own MCP server,
so tool names follow the pattern:

    mcp__<category>__<tool_name>

For example, the calendar tool below is "mcp__schedule__get_calendar".
See TOOL_CATALOG at the bottom for the full mapping.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from claude_agent_sdk import tool, create_sdk_mcp_server


# ──────────────────────────────────────────────────────────────────────────────
# Data loading — each breakout supplies its own data/ directory. The path is
# set at runtime by agent_base.py before any tools are called.
# ──────────────────────────────────────────────────────────────────────────────

_DATA_DIR: Path | None = None


def set_data_dir(path: Path) -> None:
    """Called by agent_base.py at startup to point tools at the right
    breakout's mock data."""
    global _DATA_DIR
    _DATA_DIR = path


def _load(filename: str) -> dict | list:
    """Load a JSON data file from the current breakout's data/ directory.
    Returns {} if the file doesn't exist — lets breakouts opt out of data
    they don't need without causing errors."""
    if _DATA_DIR is None:
        return {}
    path = _DATA_DIR / filename
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _text_result(text: str) -> dict:
    """Standard tool result wrapper."""
    return {"content": [{"type": "text", "text": text}]}


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY: schedule
# Calendar and scheduling tools. Useful for chief-of-staff agents.
# ══════════════════════════════════════════════════════════════════════════════


@tool(
    "get_calendar",
    "Retrieve calendar events for a date range. Dates should be in "
    "YYYY-MM-DD format. Use this to see what's on the user's schedule.",
    {"start_date": str, "end_date": str},
)
async def get_calendar(args: dict) -> dict:
    events = _load("calendar.json")
    if not events:
        return _text_result("No calendar data available.")

    start = args.get("start_date", "")
    end = args.get("end_date", "")

    filtered = [
        e for e in events
        if (not start or e.get("date", "") >= start)
        and (not end or e.get("date", "") <= end)
    ]
    if not filtered:
        return _text_result(f"No events between {start} and {end}.")

    lines = [f"Calendar ({start} to {end}):"]
    for e in filtered:
        lines.append(
            f"  {e.get('date')} {e.get('time', '')} — {e.get('title')} "
            f"[{', '.join(e.get('attendees', []))}]"
        )
        if e.get("notes"):
            lines.append(f"    Notes: {e['notes']}")
    return _text_result("\n".join(lines))


@tool(
    "find_meeting_slot",
    "Find an open slot on the calendar for a meeting of a given duration "
    "(in minutes). Returns the earliest available slot in the requested "
    "date range.",
    {"duration_minutes": int, "start_date": str, "end_date": str},
)
async def find_meeting_slot(args: dict) -> dict:
    # Simple mock: return a plausible slot. A real implementation would
    # actually check the calendar for conflicts.
    duration = args.get("duration_minutes", 30)
    start = args.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    return _text_result(
        f"Found open slot: {start} at 14:00 for {duration} minutes. "
        f"(No conflicts detected in current calendar data.)"
    )


@tool(
    "draft_email",
    "Draft an email. This does NOT send — it returns the draft for review. "
    "Never claim an email was sent; always return the draft for human approval.",
    {"to": str, "subject": str, "body": str},
)
async def draft_email(args: dict) -> dict:
    to = args.get("to", "")
    subject = args.get("subject", "")
    body = args.get("body", "")
    draft = (
        f"═══ EMAIL DRAFT (not sent — awaiting approval) ═══\n"
        f"To: {to}\n"
        f"Subject: {subject}\n\n"
        f"{body}\n"
        f"═══════════════════════════════════════════════════"
    )
    return _text_result(draft)


schedule_server = create_sdk_mcp_server(
    name="schedule", version="1.0.0",
    tools=[get_calendar, find_meeting_slot, draft_email],
)


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY: knowledge
# Document and knowledge-base search. Useful for customer support and
# chief-of-staff agents.
# ══════════════════════════════════════════════════════════════════════════════


@tool(
    "search_knowledge_base",
    "Search the internal knowledge base for articles matching a query. "
    "Returns article titles and snippets. Use this before answering "
    "customer questions to check for existing documentation.",
    {"query": str},
)
async def search_knowledge_base(args: dict) -> dict:
    kb = _load("knowledge_base.json")
    if not kb:
        return _text_result("Knowledge base is empty.")

    query = args.get("query", "").lower()
    matches = [
        article for article in kb
        if query in article.get("title", "").lower()
        or query in article.get("body", "").lower()
        or any(query in tag.lower() for tag in article.get("tags", []))
    ]

    if not matches:
        return _text_result(f"No articles matching '{query}'.")

    lines = [f"Found {len(matches)} article(s):"]
    for a in matches:
        snippet = a.get("body", "")[:150]
        lines.append(f"\n• {a.get('title')} (ID: {a.get('id')})")
        lines.append(f"  {snippet}...")
    return _text_result("\n".join(lines))


@tool(
    "read_document",
    "Read the full contents of a document or knowledge-base article by ID.",
    {"document_id": str},
)
async def read_document(args: dict) -> dict:
    kb = _load("knowledge_base.json")
    docs = _load("documents.json")
    all_docs = (kb if isinstance(kb, list) else []) + (docs if isinstance(docs, list) else [])

    doc_id = args.get("document_id", "")
    for d in all_docs:
        if d.get("id") == doc_id:
            return _text_result(
                f"# {d.get('title')}\n\n{d.get('body', '(no content)')}"
            )
    return _text_result(f"Document '{doc_id}' not found.")


knowledge_server = create_sdk_mcp_server(
    name="knowledge", version="1.0.0",
    tools=[search_knowledge_base, read_document],
)


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY: support
# Customer and ticket management. Core of the customer-support breakout.
# ══════════════════════════════════════════════════════════════════════════════


@tool(
    "lookup_customer",
    "Look up a customer's account details by customer ID or email. "
    "Returns plan tier, account status, and recent activity.",
    {"customer_identifier": str},
)
async def lookup_customer(args: dict) -> dict:
    customers = _load("customers.json")
    if not customers:
        return _text_result("No customer data available.")

    identifier = args.get("customer_identifier", "").lower()
    for c in customers:
        if (
            c.get("id", "").lower() == identifier
            or c.get("email", "").lower() == identifier
        ):
            return _text_result(json.dumps(c, indent=2))
    return _text_result(f"Customer '{identifier}' not found.")


@tool(
    "get_ticket",
    "Retrieve a support ticket by ID. Returns the customer's issue, "
    "conversation history, and current status.",
    {"ticket_id": str},
)
async def get_ticket(args: dict) -> dict:
    tickets = _load("tickets.json")
    if not tickets:
        return _text_result("No ticket data available.")

    ticket_id = args.get("ticket_id", "")
    for t in tickets:
        if t.get("id") == ticket_id:
            return _text_result(json.dumps(t, indent=2))
    return _text_result(f"Ticket '{ticket_id}' not found.")


@tool(
    "list_open_tickets",
    "List all currently open support tickets, optionally filtered by "
    "priority ('low', 'medium', 'high', 'critical').",
    {"priority": str},
)
async def list_open_tickets(args: dict) -> dict:
    tickets = _load("tickets.json")
    if not tickets:
        return _text_result("No ticket data available.")

    priority = args.get("priority", "").lower()
    open_tickets = [
        t for t in tickets
        if t.get("status") == "open"
        and (not priority or t.get("priority", "").lower() == priority)
    ]

    if not open_tickets:
        return _text_result(
            f"No open tickets{' at priority ' + priority if priority else ''}."
        )

    lines = [f"Open tickets ({len(open_tickets)}):"]
    for t in open_tickets:
        lines.append(
            f"  [{t.get('priority', '?').upper()}] {t.get('id')} — "
            f"{t.get('subject')} ({t.get('customer_id')})"
        )
    return _text_result("\n".join(lines))


@tool(
    "add_ticket_note",
    "Add an internal note to a support ticket. Notes are visible to support "
    "staff but NOT to the customer. Use this to record your reasoning or "
    "next steps.",
    {"ticket_id": str, "note": str},
)
async def add_ticket_note(args: dict) -> dict:
    ticket_id = args.get("ticket_id", "")
    note = args.get("note", "")
    # In production this would write to the ticketing system. Here we just
    # confirm the note — the workshop is about the pattern, not persistence.
    return _text_result(
        f"Internal note added to {ticket_id}:\n  \"{note}\"\n"
        f"(visible to support staff only)"
    )


support_server = create_sdk_mcp_server(
    name="support", version="1.0.0",
    tools=[lookup_customer, get_ticket, list_open_tickets, add_ticket_note],
)


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY: ops
# Observability and incident management. Core of the SRE breakout.
# ══════════════════════════════════════════════════════════════════════════════


@tool(
    "get_service_status",
    "Get the current health status of a service. Returns overall state "
    "and any active alerts.",
    {"service": str},
)
async def get_service_status(args: dict) -> dict:
    services = _load("services.json")
    if not services:
        return _text_result("No service data available.")

    service_name = args.get("service", "").lower()
    for s in services:
        if s.get("name", "").lower() == service_name:
            return _text_result(json.dumps(s, indent=2))
    return _text_result(
        f"Service '{service_name}' not found. Known services: "
        f"{', '.join(s.get('name', '?') for s in services)}"
    )


@tool(
    "query_metrics",
    "Query a time-series metric for a service. Returns recent data points. "
    "Common metrics: 'error_rate', 'latency_p99', 'requests_per_second', "
    "'cpu_utilization'.",
    {"service": str, "metric": str, "last_minutes": int},
)
async def query_metrics(args: dict) -> dict:
    service = args.get("service", "")
    metric = args.get("metric", "")
    minutes = args.get("last_minutes", 15)

    # Generate plausible mock data. Seed by service+metric so results are
    # stable across calls (the agent should see consistent numbers).
    random.seed(hash(f"{service}:{metric}"))
    baseline = {
        "error_rate": (0.2, 0.5),  # percent
        "latency_p99": (120, 40),  # ms
        "requests_per_second": (850, 200),
        "cpu_utilization": (45, 15),  # percent
    }.get(metric, (100, 30))

    now = datetime.now()
    points = []
    for i in range(minutes):
        ts = (now - timedelta(minutes=minutes - i)).strftime("%H:%M")
        val = round(random.gauss(baseline[0], baseline[1] / 3), 2)
        points.append(f"  {ts}  {val}")

    # Inject an anomaly for the checkout service to give the SRE agent
    # something interesting to find.
    if service.lower() == "checkout" and metric == "error_rate":
        points[-3] = f"  {points[-3].split()[0]}  4.80  ← SPIKE"
        points[-2] = f"  {points[-2].split()[0]}  5.10  ← SPIKE"
        points[-1] = f"  {points[-1].split()[0]}  4.95  ← SPIKE"

    return _text_result(
        f"{metric} for {service} (last {minutes}m):\n" + "\n".join(points)
    )


@tool(
    "get_recent_alerts",
    "List alerts fired in the recent past. Optionally filter by service.",
    {"service": str, "last_hours": int},
)
async def get_recent_alerts(args: dict) -> dict:
    alerts = _load("alerts.json")
    if not alerts:
        return _text_result("No alert data available.")

    service = args.get("service", "").lower()
    filtered = [
        a for a in alerts
        if not service or a.get("service", "").lower() == service
    ]

    if not filtered:
        return _text_result(
            f"No recent alerts{' for ' + service if service else ''}."
        )

    lines = [f"Recent alerts ({len(filtered)}):"]
    for a in filtered:
        lines.append(
            f"  [{a.get('severity', '?').upper()}] {a.get('fired_at')} — "
            f"{a.get('service')}: {a.get('message')}"
        )
    return _text_result("\n".join(lines))


@tool(
    "search_runbooks",
    "Search the runbook library for procedures matching a query. Returns "
    "titles and summaries — use read_runbook to get the full procedure.",
    {"query": str},
)
async def search_runbooks(args: dict) -> dict:
    runbooks = _load("runbooks.json")
    if not runbooks:
        return _text_result("No runbooks available.")

    query = args.get("query", "").lower()
    matches = [
        r for r in runbooks
        if query in r.get("title", "").lower()
        or query in r.get("summary", "").lower()
    ]

    if not matches:
        return _text_result(f"No runbooks matching '{query}'.")

    lines = [f"Found {len(matches)} runbook(s):"]
    for r in matches:
        lines.append(f"  {r.get('id')} — {r.get('title')}: {r.get('summary')}")
    return _text_result("\n".join(lines))


@tool(
    "read_runbook",
    "Read the full step-by-step procedure for a runbook by ID.",
    {"runbook_id": str},
)
async def read_runbook(args: dict) -> dict:
    runbooks = _load("runbooks.json")
    if not runbooks:
        return _text_result("No runbooks available.")

    rb_id = args.get("runbook_id", "")
    for r in runbooks:
        if r.get("id") == rb_id:
            steps = "\n".join(
                f"  {i+1}. {s}" for i, s in enumerate(r.get("steps", []))
            )
            return _text_result(
                f"# {r.get('title')}\n\n{r.get('summary')}\n\nSteps:\n{steps}"
            )
    return _text_result(f"Runbook '{rb_id}' not found.")


ops_server = create_sdk_mcp_server(
    name="ops", version="1.0.0",
    tools=[
        get_service_status, query_metrics, get_recent_alerts,
        search_runbooks, read_runbook,
    ],
)


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY: code
# Repository inspection. Core of the coding-agent breakout.
# ══════════════════════════════════════════════════════════════════════════════


@tool(
    "list_files",
    "List files in the workspace directory. Optionally filter by substring.",
    {"pattern": str},
)
async def list_files(args: dict) -> dict:
    if _DATA_DIR is None:
        return _text_result("Workspace not configured.")
    # For the coding agent, _DATA_DIR points at a workspace/ directory of
    # actual code files rather than JSON.
    pattern = args.get("pattern", "").lower()
    files = sorted(
        str(p.relative_to(_DATA_DIR))
        for p in _DATA_DIR.rglob("*")
        if p.is_file() and (not pattern or pattern in p.name.lower())
    )
    if not files:
        return _text_result(
            f"No files matching '{pattern}'." if pattern else "Workspace is empty."
        )
    return _text_result("\n".join(files))


@tool(
    "read_file",
    "Read the full contents of a file in the workspace.",
    {"path": str},
)
async def read_file(args: dict) -> dict:
    if _DATA_DIR is None:
        return _text_result("Workspace not configured.")
    path = args.get("path", "")
    full = _DATA_DIR / path
    # Basic path-traversal guard — stay inside the workspace.
    try:
        full.resolve().relative_to(_DATA_DIR.resolve())
    except ValueError:
        return _text_result("Path is outside the workspace.")
    if not full.exists():
        return _text_result(f"File not found: {path}")
    return _text_result(full.read_text())


@tool(
    "search_code",
    "Search for a string across all files in the workspace. Returns "
    "matching lines with file and line number.",
    {"query": str},
)
async def search_code(args: dict) -> dict:
    if _DATA_DIR is None:
        return _text_result("Workspace not configured.")
    query = args.get("query", "")
    if not query:
        return _text_result("Empty query.")

    hits = []
    for p in _DATA_DIR.rglob("*"):
        if not p.is_file():
            continue
        try:
            for i, line in enumerate(p.read_text().splitlines(), 1):
                if query in line:
                    rel = p.relative_to(_DATA_DIR)
                    hits.append(f"  {rel}:{i}: {line.strip()}")
        except UnicodeDecodeError:
            continue

    if not hits:
        return _text_result(f"No matches for '{query}'.")
    return _text_result(f"Found {len(hits)} match(es):\n" + "\n".join(hits[:50]))


code_server = create_sdk_mcp_server(
    name="code", version="1.0.0",
    tools=[list_files, read_file, search_code],
)


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY: memory
# Same persistent-memory pattern as the guided demo, factored into a reusable
# category so any breakout can enable it.
# ══════════════════════════════════════════════════════════════════════════════


def _memory_path() -> Path:
    # Store memory alongside the breakout's data so each breakout has its own.
    base = _DATA_DIR if _DATA_DIR else Path.cwd()
    return base / "memory_store.json"


def _read_memory() -> list[dict]:
    p = _memory_path()
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return []


@tool(
    "save_memory",
    "Save a note to persistent memory for use in future conversations. "
    "Use for user preferences and important context that should survive "
    "between sessions.",
    {"category": str, "note": str},
)
async def save_memory(args: dict) -> dict:
    category = args.get("category", "general").strip() or "general"
    note = args.get("note", "").strip()
    if not note:
        return _text_result("Empty note — nothing saved.")

    memories = _read_memory()
    memories.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "category": category,
        "note": note,
    })
    if len(memories) > 50:
        memories = memories[-50:]
    _memory_path().write_text(json.dumps(memories, indent=2))
    return _text_result(f"Saved to memory under '{category}'.")


@tool(
    "list_memories",
    "List everything currently stored in persistent memory.",
    {},
)
async def list_memories(args: dict) -> dict:
    del args
    memories = _read_memory()
    if not memories:
        return _text_result("Memory is empty.")
    lines = ["Current memories:"]
    for m in memories:
        lines.append(f"[{m['category']}] {m['note']}  (saved {m['timestamp']})")
    return _text_result("\n".join(lines))


memory_server = create_sdk_mcp_server(
    name="memory", version="1.0.0",
    tools=[save_memory, list_memories],
)


def load_memory_context() -> str:
    """Used by agent_base.py to inject memories into the system prompt."""
    memories = _read_memory()
    if not memories:
        return ""
    lines = ["MEMORIES FROM PREVIOUS SESSIONS:"]
    for m in memories:
        lines.append(f"- [{m['category']}] {m['note']}")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# TOOL CATALOG
#
# This is what each breakout's config.py imports. Each entry maps a category
# name to (mcp_server, list_of_full_tool_names). Your config just lists the
# categories it wants — agent_base.py handles the rest.
# ══════════════════════════════════════════════════════════════════════════════

TOOL_CATALOG = {
    "schedule": (
        schedule_server,
        [
            "mcp__schedule__get_calendar",
            "mcp__schedule__find_meeting_slot",
            "mcp__schedule__draft_email",
        ],
    ),
    "knowledge": (
        knowledge_server,
        [
            "mcp__knowledge__search_knowledge_base",
            "mcp__knowledge__read_document",
        ],
    ),
    "support": (
        support_server,
        [
            "mcp__support__lookup_customer",
            "mcp__support__get_ticket",
            "mcp__support__list_open_tickets",
            "mcp__support__add_ticket_note",
        ],
    ),
    "ops": (
        ops_server,
        [
            "mcp__ops__get_service_status",
            "mcp__ops__query_metrics",
            "mcp__ops__get_recent_alerts",
            "mcp__ops__search_runbooks",
            "mcp__ops__read_runbook",
        ],
    ),
    "code": (
        code_server,
        [
            "mcp__code__list_files",
            "mcp__code__read_file",
            "mcp__code__search_code",
        ],
    ),
    "memory": (
        memory_server,
        [
            "mcp__memory__save_memory",
            "mcp__memory__list_memories",
        ],
    ),
}
