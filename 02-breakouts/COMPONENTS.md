# Component Reference

The full menu of pre-built components available in every breakout's `config.py`.

---

## Tool categories

Set via `TOOL_CATEGORIES = [...]` in your breakout's config.

| Category | Tools | Reads from | Useful for |
|---|---|---|---|
| **`schedule`** | `get_calendar`, `find_meeting_slot`, `draft_email` | `calendar.json` | Chief of staff, exec assistants |
| **`knowledge`** | `search_knowledge_base`, `read_document` | `knowledge_base.json`, `documents.json` | Any agent that cites internal docs |
| **`support`** | `lookup_customer`, `get_ticket`, `list_open_tickets`, `add_ticket_note` | `customers.json`, `tickets.json` | Customer support, account management |
| **`ops`** | `get_service_status`, `query_metrics`, `get_recent_alerts`, `search_runbooks`, `read_runbook` | `services.json`, `alerts.json`, `runbooks.json` | SRE, incident response |
| **`code`** | `list_files`, `read_file`, `search_code` | *(any directory)* | Codebase exploration |
| **`memory`** | `save_memory`, `list_memories` | *(writes `memory_store.json`)* | Anything that should improve over time |

Full tool names follow `mcp__<category>__<tool>` — e.g., `mcp__support__lookup_customer`.

**Source:** [`_shared/tool_library.py`](./_shared/tool_library.py)

---

## Sub-agents

Set via `SUBAGENTS = [...]` in your breakout's config.

| Name | Role | Needs tool categories | Model |
|---|---|---|---|
| **`researcher`** | Gathers info on a focused question | `knowledge` (at minimum) | haiku |
| **`summarizer`** | Condenses long content into key points | *(none)* | haiku |
| **`classifier`** | Categorizes / routes items | *(none)* | haiku |
| **`verifier`** | Fact-checks specific claims | `knowledge` | haiku |
| **`writer`** | Polishes rough notes into clean prose | *(none)* | haiku |
| **`procedure_runner`** | Walks through checklists step by step | `ops` | haiku |

If you enable a sub-agent without its required tool categories, it still runs but has nothing to work with. The runner prints a warning when it detects this.

**Source:** [`_shared/subagent_library.py`](./_shared/subagent_library.py)

---

## Other config knobs

| Knob | Default | What it does |
|---|---|---|
| `SYSTEM_PROMPT` | *(varies)* | The main agent's instructions — where most iteration happens |
| `DEFAULT_TASK` | *(varies)* | Shown when you press Enter at the prompt |
| `MODEL` | `"claude-sonnet-4-6"` | Main agent model (`"claude-opus-4-6"` for quality, `"claude-haiku-4-5"` for speed) |
| `VERBOSITY` | `"verbose"` | `"verbose"` shows tool calls; `"normal"` hides them |
| `MAX_TURNS` | `30` | Safety cap on the agentic loop |

---

## How it fits together

Your `config.py` → `_shared/agent_base.py:_build_options()` → `ClaudeAgentOptions` → SDK.

The `_build_options()` function is the same pattern as `01-guided-demo/agent.py:build_options()` from the guided demo — compare them side by side to see how the Lego-assembly version generalizes the flip-a-switch version.
