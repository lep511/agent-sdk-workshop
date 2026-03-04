"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   FREEFORM AGENT — BLANK CANVAS                                              ║
║                                                                              ║
║   Pick any combination of components and write any prompt. This is the       ║
║   "I have my own use case" breakout.                                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

You've got the full menu. Nothing is pre-selected. Build whatever you want.

─── Full component reference ─────────────────────────────────────────────────

TOOL CATEGORIES (from _shared/tool_library.py):

  "schedule"   — get_calendar, find_meeting_slot, draft_email
                 (uses data/calendar.json if you provide it)

  "knowledge"  — search_knowledge_base, read_document
                 (uses data/knowledge_base.json + data/documents.json)

  "support"    — lookup_customer, get_ticket, list_open_tickets, add_ticket_note
                 (uses data/customers.json + data/tickets.json)

  "ops"        — get_service_status, query_metrics, get_recent_alerts,
                 search_runbooks, read_runbook
                 (uses data/services.json + data/alerts.json + data/runbooks.json)

  "code"       — list_files, read_file, search_code
                 (operates on whatever DATA_DIR points at — real files, not JSON)

  "memory"     — save_memory, list_memories
                 (persists to data/memory_store.json between runs)

SUB-AGENTS (from _shared/subagent_library.py):

  "researcher"       — gathers info, works best with "knowledge"
  "summarizer"       — condenses long content, no tools needed
  "classifier"       — categorizes things, no tools needed
  "verifier"         — fact-checks claims, works best with "knowledge"
  "writer"           — polishes prose, no tools needed
  "procedure_runner" — walks through checklists, works best with "ops"

─── Data note ────────────────────────────────────────────────────────────────

Each tool category reads from specific JSON files in ./data/. You can:

  a) Copy data files from another breakout to reuse their scenario
  b) Write your own JSON files matching the shapes
  c) Enable categories with no data and watch the agent handle empty results
     (spoiler: it handles it fine, just has less to work with)

Check data/README.md for the expected file shapes, or ../COMPONENTS.md for
the full component reference.
"""

from pathlib import Path

AGENT_NAME = "Freeform Agent"


# ──────────────────────────────────────────────────────────────────────────────
# COMPONENT SELECTION — pick your own
# ──────────────────────────────────────────────────────────────────────────────

TOOL_CATEGORIES: list[str] = [
    # "knowledge",
    # "schedule",
    # "support",
    # "ops",
    # "code",
    # "memory",
]

SUBAGENTS: list[str] = [
    # "researcher",
    # "summarizer",
    # "classifier",
    # "verifier",
    # "writer",
    # "procedure_runner",
]


# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT — write your own
#
# Blank slate. A few prompt-engineering patterns that work well with the SDK:
#
#   1. Give it a role and a goal:
#      "You are a [role]. Your job is to [goal]."
#
#   2. Describe the workflow in numbered steps:
#      "When asked to X: 1) ... 2) ... 3) ..."
#
#   3. Tell it how to use its sub-agents (if you enabled any):
#      "Delegate [specific task type] to the [sub-agent name] sub-agent."
#
#   4. Shape the output:
#      "Structure your responses as: [sections]"
#
#   5. Add guardrails:
#      "Never [bad thing]. If asked to, [alternative behavior] instead."
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
"""


DEFAULT_TASK = "Hello — what can you help me with?"


# ──────────────────────────────────────────────────────────────────────────────
# KNOBS
# ──────────────────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-6"
VERBOSITY = "verbose"
MAX_TURNS = 30


# ══════════════════════════════════════════════════════════════════════════════
DATA_DIR = Path(__file__).parent / "data"
