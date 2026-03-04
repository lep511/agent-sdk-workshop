"""
Persistent memory layer — Guided Demo, Stage 3.

"Memory" here means: things the agent should remember between completely
separate runs of the script. Close the terminal, come back tomorrow, and
it still knows you prefer bullet points.

We implement this with two pieces that work together:

  1. A save_memory TOOL the agent can call to write things down
     ("User wants briefings under 300 words")

  2. A UserPromptSubmit HOOK that fires at the start of each turn, reads
     the memory file, and injects whatever's in there as additional context

The store is a plain JSON file next to this module. Inspect it any time —
it's just a list of timestamped notes.

─── Quick vocabulary ─────────────────────────────────────────────────────────

  TOOL   Something the model can choose to call mid-turn. Defined with
         @tool, registered via an MCP server, listed in allowed_tools.

  HOOK   A Python callback that fires on SDK lifecycle events
         (UserPromptSubmit, PreToolUse, PostToolUse, etc.). The model
         doesn't choose to invoke hooks — they fire automatically.
         Registered via ClaudeAgentOptions(hooks={...}).

Both pieces are wired into the agent in agent.py when ENABLE_MEMORY is True.
"""

import json
from datetime import datetime
from pathlib import Path

from claude_agent_sdk import tool, create_sdk_mcp_server, HookMatcher
from claude_agent_sdk.types import HookContext, HookInput, HookJSONOutput

# ──────────────────────────────────────────────────────────────────────────────
# Storage — a single JSON file right next to this module
# ──────────────────────────────────────────────────────────────────────────────

_MEMORY_PATH = Path(__file__).parent / "memory_store.json"


def _read_memories() -> list[dict]:
    if not _MEMORY_PATH.exists():
        return []
    try:
        return json.loads(_MEMORY_PATH.read_text())
    except json.JSONDecodeError:
        # Corrupted file — start fresh rather than crash the workshop.
        return []


def _write_memories(memories: list[dict]) -> None:
    _MEMORY_PATH.write_text(json.dumps(memories, indent=2))


def load_memory_summary() -> str:
    """Human-readable summary of what's currently remembered.

    Called from agent.py at startup so attendees can see the memory state
    in the console before the agent runs.
    """
    memories = _read_memories()
    if not memories:
        return ""
    lines = []
    for m in memories:
        lines.append(f"  • [{m['category']}] {m['note']}  ({m['timestamp']})")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Part 1: the save_memory TOOL
#
# The agent calls this when it wants to remember something. We also expose
# list_memories so it can check what it already knows before saving a
# duplicate.
# ──────────────────────────────────────────────────────────────────────────────


@tool(
    "save_memory",
    "Save a note to persistent memory so it's available in future "
    "conversations. Use for user preferences (e.g., 'prefers bullets'), "
    "important facts about recurring topics, or summaries of briefings "
    "you've produced. Don't save transient details — only things worth "
    "remembering next week.",
    {"category": str, "note": str},
)
async def save_memory(args: dict) -> dict:
    category = args.get("category", "general").strip() or "general"
    note = args.get("note", "").strip()

    if not note:
        return {
            "content": [{"type": "text", "text": "Empty note — nothing saved."}]
        }

    memories = _read_memories()
    memories.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "category": category,
            "note": note,
        }
    )
    # Keep the store from growing unbounded during a long workshop.
    if len(memories) > 50:
        memories = memories[-50:]
    _write_memories(memories)

    return {
        "content": [
            {"type": "text", "text": f"Saved to memory under '{category}'."}
        ]
    }


@tool(
    "list_memories",
    "List everything currently in persistent memory. Use this if you want "
    "to check what you already remember before saving something new.",
    {},
)
async def list_memories(args: dict) -> dict:
    memories = _read_memories()
    if not memories:
        return {
            "content": [{"type": "text", "text": "Memory is empty."}]
        }
    lines = ["Current memories:"]
    for m in memories:
        lines.append(f"[{m['category']}] {m['note']}  (saved {m['timestamp']})")
    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


def make_memory_server():
    """Build the MCP server bundle. Wrapped in a function (rather than a
    module-level constant) so importing this module doesn't have the side
    effect of constructing an MCP server when memory is disabled."""
    return create_sdk_mcp_server(
        name="memory",
        version="1.0.0",
        tools=[save_memory, list_memories],
    )


MEMORY_TOOL_NAMES = [
    "mcp__memory__save_memory",
    "mcp__memory__list_memories",
]


# ──────────────────────────────────────────────────────────────────────────────
# Part 2: the memory-injection HOOK
#
# Hooks are Python callbacks that fire on SDK lifecycle events. This one
# fires on UserPromptSubmit — i.e., right when the user's message is about
# to be sent to the model. We read the memory file and attach its contents
# as additionalContext, which the SDK weaves into the system context.
#
# The model never "calls" a hook — it fires automatically. This is the
# complement to the tool: the tool WRITES memory, the hook READS it.
# ──────────────────────────────────────────────────────────────────────────────


async def _inject_memories(
    input_data: HookInput, tool_use_id: str | None, context: HookContext
) -> HookJSONOutput:
    """Hook callback: read memory file and inject it as additional context.

    The unused parameters (input_data, tool_use_id, context) are required
    by the HookCallback signature — the SDK passes all three to every hook.
    """
    del input_data, tool_use_id, context  # required by signature, unused here

    memories = _read_memories()
    if not memories:
        # Empty dict is a valid SyncHookJSONOutput — all fields are optional.
        return {}

    lines = ["MEMORIES FROM PREVIOUS SESSIONS:"]
    for m in memories:
        lines.append(f"- [{m['category']}] {m['note']}")
    lines.append(
        "\n(Use these to personalize your response. Reference prior "
        "briefings when relevant.)"
    )

    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "\n".join(lines),
        }
    }


# HookMatcher wraps the callback. matcher=None means "fire for every
# UserPromptSubmit" (no filtering). In agent.py this gets registered as:
#   hooks = {"UserPromptSubmit": [memory_hook]}
memory_hook = HookMatcher(matcher=None, hooks=[_inject_memories])
