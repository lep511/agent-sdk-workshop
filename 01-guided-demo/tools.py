"""
Research tools for the briefing agent — Guided Demo, Stage 1.

Everything here is backed by static JSON in mock_data/. No network calls, no
external API keys, no flakiness — we want the workshop to be about the SDK
patterns, not about fighting with third-party services.

When ENABLE_TOOLS is True in config.py, these get wired into the agent via
an in-process MCP server. Look at the bottom of this file to see how.
"""

import json
from pathlib import Path

from claude_agent_sdk import tool, create_sdk_mcp_server

# ──────────────────────────────────────────────────────────────────────────────
# Mock data loading
# ──────────────────────────────────────────────────────────────────────────────

_DATA_DIR = Path(__file__).parent / "mock_data"


def _load_company(company_name: str) -> dict | None:
    """Look up a company's data file by name (fuzzy, case-insensitive)."""
    needle = company_name.lower().replace(" ", "").replace("-", "").replace("_", "")
    for path in _DATA_DIR.glob("*.json"):
        data = json.loads(path.read_text())
        hay = data.get("company", "").lower().replace(" ", "")
        if needle in hay or hay in needle:
            return data
    return None


def _known_companies() -> list[str]:
    """All company names we have mock data for."""
    companies = []
    for path in _DATA_DIR.glob("*.json"):
        data = json.loads(path.read_text())
        if "company" in data:
            companies.append(data["company"])
    return sorted(companies)


# ──────────────────────────────────────────────────────────────────────────────
# Tool definitions
#
# The @tool decorator takes three arguments:
#   1. Tool name (what the model sees)
#   2. Description (tells the model when/why to use it)
#   3. Input schema (simple dict of {param_name: python_type} — the SDK
#      converts this to JSON Schema automatically)
#
# Every tool handler is an async function that receives a dict of inputs and
# must return {"content": [{"type": "text", "text": "..."}]}.
# ──────────────────────────────────────────────────────────────────────────────


@tool(
    "search_company_news",
    "Search recent news coverage about a company. Optionally filter by topic "
    "(e.g., 'product', 'financials', 'leadership', 'acquisition'). Returns "
    "headlines and summaries from the last several months.",
    {"company": str, "topic": str},
)
async def search_company_news(args: dict) -> dict:
    company = args.get("company", "")
    topic = args.get("topic", "").lower().strip()

    data = _load_company(company)
    if data is None:
        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"No news found for '{company}'. "
                        f"Known companies: {', '.join(_known_companies())}"
                    ),
                }
            ]
        }

    news = data.get("news", [])
    if topic:
        news = [n for n in news if topic in [t.lower() for t in n.get("topics", [])]]

    if not news:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"No news matching topic '{topic}' for {data['company']}.",
                }
            ]
        }

    lines = [f"Recent news for {data['company']}:"]
    for item in news:
        lines.append(f"\n[{item['date']}] {item['headline']}")
        lines.append(f"  {item['summary']}")

    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


@tool(
    "get_company_financials",
    "Retrieve the most recent financial snapshot for a company: revenue, "
    "growth rate, margins, cash position, and funding history. Use this to "
    "ground any claims about financial health.",
    {"company": str},
)
async def get_company_financials(args: dict) -> dict:
    company = args.get("company", "")

    data = _load_company(company)
    if data is None:
        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"No financial data for '{company}'. "
                        f"Known companies: {', '.join(_known_companies())}"
                    ),
                }
            ]
        }

    fin = data.get("financials", {})
    # Return the raw structure — the model is good at parsing JSON and this
    # is easier to maintain than custom formatting.
    payload = {
        "company": data["company"],
        "industry": data.get("industry"),
        "employees": data.get("employees"),
        "financials": fin,
    }
    return {
        "content": [{"type": "text", "text": json.dumps(payload, indent=2)}]
    }


@tool(
    "get_recent_press_releases",
    "Get recent official press releases issued by a company. These are the "
    "company's own words — useful for understanding how they position "
    "announcements, and for direct quotes.",
    {"company": str},
)
async def get_recent_press_releases(args: dict) -> dict:
    company = args.get("company", "")

    data = _load_company(company)
    if data is None:
        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"No press releases for '{company}'. "
                        f"Known companies: {', '.join(_known_companies())}"
                    ),
                }
            ]
        }

    releases = data.get("press_releases", [])
    if not releases:
        return {
            "content": [
                {"type": "text", "text": f"No press releases found for {data['company']}."}
            ]
        }

    lines = [f"Press releases from {data['company']}:"]
    for pr in releases:
        lines.append(f"\n═══ {pr['date']} — {pr['title']} ═══")
        lines.append(pr["body"])

    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


@tool(
    "get_competitive_landscape",
    "Get a summary of a company's competitive positioning: who they compete "
    "against, how they differentiate, and rough market share.",
    {"company": str},
)
async def get_competitive_landscape(args: dict) -> dict:
    company = args.get("company", "")

    data = _load_company(company)
    if data is None:
        return {
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"No competitive data for '{company}'. "
                        f"Known companies: {', '.join(_known_companies())}"
                    ),
                }
            ]
        }

    comp = data.get("competitive_landscape", {})
    payload = {"company": data["company"], "competitive_landscape": comp}
    return {
        "content": [{"type": "text", "text": json.dumps(payload, indent=2)}]
    }


# ──────────────────────────────────────────────────────────────────────────────
# Bundle into an in-process MCP server
#
# This is the SDK's way of packaging a set of tools. The server runs in the
# same Python process as the agent — no subprocess, no IPC overhead. Your
# tool functions have direct access to any state in this module (closures,
# module-level variables, etc.).
#
# In agent.py we pass this server to ClaudeAgentOptions(mcp_servers={...})
# and list each tool's full name in allowed_tools. The naming convention is:
#
#     mcp__<server_key>__<tool_name>
#
# So if agent.py registers this as mcp_servers={"research": research_server},
# the tool below becomes "mcp__research__search_company_news".
# ──────────────────────────────────────────────────────────────────────────────

research_server = create_sdk_mcp_server(
    name="research",
    version="1.0.0",
    tools=[
        search_company_news,
        get_company_financials,
        get_recent_press_releases,
        get_competitive_landscape,
    ],
)

# The list of tool names to put in ClaudeAgentOptions.allowed_tools.
# Exported here so agent.py doesn't have to hardcode the list.
RESEARCH_TOOL_NAMES = [
    "mcp__research__search_company_news",
    "mcp__research__get_company_financials",
    "mcp__research__get_recent_press_releases",
    "mcp__research__get_competitive_landscape",
]
