"""
Example 3: Multi-Agent Orchestrator

A parent durable function that fans out work to multiple specialized Claude
agents (each running as its own durable step with the full SDK), then
synthesizes their results.

Each sub-agent is independently checkpointed. If Lambda crashes after 2/3
agents complete, only the 3rd re-runs on replay.

This example also demonstrates AgentDefinition for SDK-native sub-agents
within a single step (Option A in the orchestrator pattern).
"""

import json
import sys
from pathlib import Path

from aws_durable_execution_sdk_python import durable_execution, DurableContext
from claude_agent_sdk import tool, create_sdk_mcp_server, AgentDefinition

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lib.claude_durable import run_multi_agent


# ---------------------------------------------------------------------------
# MCP Tools for specialized agents
# ---------------------------------------------------------------------------

@tool("search_financials", "Search for financial data about a company.", {
    "company": str,
})
async def search_financials(args: dict) -> dict:
    """Mock financial data search."""
    company = args["company"]
    data = {
        "company": company,
        "revenue": "$4.2B (FY2025)",
        "growth": "+18% YoY",
        "margin": "23% operating",
        "guidance": "Raised FY2026 outlook to $5.0B",
    }
    return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}


@tool("search_news", "Search recent news articles about a company.", {
    "company": str,
    "topic": str,
})
async def search_news(args: dict) -> dict:
    """Mock news search."""
    company = args["company"]
    articles = [
        {
            "title": f"{company} announces new AI partnership",
            "date": "2025-05-10",
            "source": "TechCrunch",
            "summary": f"{company} partnered with a major cloud provider to integrate AI.",
        },
        {
            "title": f"{company} Q1 earnings beat expectations",
            "date": "2025-04-28",
            "source": "Reuters",
            "summary": "Revenue up 18% with strong enterprise demand driving growth.",
        },
    ]
    return {"content": [{"type": "text", "text": json.dumps(articles, indent=2)}]}


@tool("search_competitors", "Find competitor landscape for a company.", {
    "company": str,
})
async def search_competitors(args: dict) -> dict:
    """Mock competitor search."""
    company = args["company"]
    data = {
        "company": company,
        "competitors": [
            {"name": "CompetitorA", "market_share": "28%", "trend": "growing"},
            {"name": "CompetitorB", "market_share": "15%", "trend": "stable"},
        ],
        "company_market_share": "22%",
        "competitive_position": "Strong #2, gaining on leader",
    }
    return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}


# Bundle all tools into a single research server
research_server = create_sdk_mcp_server(
    name="research",
    tools=[search_financials, search_news, search_competitors],
)


# ---------------------------------------------------------------------------
# Sub-agent configurations (explicit fan-out pattern)
# ---------------------------------------------------------------------------

def build_sub_agents(company: str) -> dict[str, dict]:
    """Build sub-agent configs for the given company."""
    return {
        "financial_analyst": {
            "prompt": f"Analyze the financial health of {company}. Use your tools to gather data, then provide 3-4 bullet points on revenue, growth, margins, and guidance.",
            "system": (
                "You are a financial analyst. Be concise — 3-4 bullet points max. "
                "Always cite specific numbers."
            ),
            "mcp_servers": {"research": research_server},
            "allowed_tools": ["mcp__research__search_financials"],
            "max_turns": 3,
        },
        "news_analyst": {
            "prompt": f"Find and summarize the most important recent developments for {company}. Focus on strategic moves, partnerships, and market events. 3-4 bullet points.",
            "system": (
                "You are a news analyst. Focus on strategic significance, not "
                "trivia. 3-4 bullet points max."
            ),
            "mcp_servers": {"research": research_server},
            "allowed_tools": ["mcp__research__search_news"],
            "max_turns": 3,
        },
        "competitive_analyst": {
            "prompt": f"Assess {company}'s market position, key competitors, and competitive dynamics. 3-4 bullet points.",
            "system": (
                "You are a competitive intelligence analyst. Assess positioning "
                "and trends. 3-4 bullet points max."
            ),
            "mcp_servers": {"research": research_server},
            "allowed_tools": ["mcp__research__search_competitors"],
            "max_turns": 3,
        },
    }


# ---------------------------------------------------------------------------
# Lambda handler — orchestrator
# ---------------------------------------------------------------------------

SYNTHESIS_PROMPT = """\
Below are research findings from three specialized analysts. Synthesize them
into a single, coherent executive briefing that:
1. Leads with the most important insight
2. Connects the financial, news, and competitive threads
3. Ends with 2-3 key questions the executive should ask in their meeting

Keep it under 300 words.

## Financial Analysis
{financial_analyst}

## Recent Developments
{news_analyst}

## Competitive Position
{competitive_analyst}
"""


@durable_execution
def handler(event: dict, context: DurableContext) -> dict:
    """Orchestrator: fans out to sub-agents via durable steps, then synthesizes."""
    company = event.get("company", "Acme Corp")

    context.logger.info("Starting multi-agent orchestration", extra={"company": company})

    result = run_multi_agent(
        context,
        sub_agents=build_sub_agents(company),
        synthesis_prompt=SYNTHESIS_PROMPT,
        synthesis_system="You are a senior analyst writing an executive briefing. Be direct and actionable.",
    )

    result["company"] = company
    context.logger.info("Orchestration complete")
    return result
