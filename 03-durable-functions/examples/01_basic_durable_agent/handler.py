"""
Example 1: Basic Durable Agent

A Claude agent that searches and summarizes using the full Claude Agent SDK —
with MCP tools, proper tool definitions, and the SDK's built-in agent loop.
The entire agent session is checkpointed as a single durable step.

Deploy and invoke:
    aws lambda invoke --function-name basic-durable-agent:live \
      --payload '{"prompt": "What are the key features of AWS Lambda durable functions?"}' \
      --cli-binary-format raw-in-base64-out response.json
"""

import json
import sys
from pathlib import Path

from aws_durable_execution_sdk_python import durable_execution, DurableContext
from claude_agent_sdk import tool, create_sdk_mcp_server

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lib.claude_durable import run_durable_agent


# ---------------------------------------------------------------------------
# MCP Tools — defined using the Claude Agent SDK @tool decorator
# ---------------------------------------------------------------------------

@tool("search_web", "Search the web for information on a topic. Returns relevant snippets.", {
    "query": str,
})
async def search_web(args: dict) -> dict:
    """Mock web search — in production, call Brave/Tavily/etc."""
    query = args["query"]
    results = [
        {
            "title": f"Result for: {query}",
            "snippet": (
                "AWS Lambda durable functions provide automatic "
                "checkpointing, retry with backoff, and execution "
                "that can span up to one year. They use a replay model "
                "to resume from the last successful step."
            ),
            "url": "https://docs.aws.amazon.com/lambda/latest/dg/durable-functions.html",
        }
    ]
    return {"content": [{"type": "text", "text": json.dumps(results, indent=2)}]}


@tool("read_document", "Fetch and read the text content of a URL or document.", {
    "url": str,
})
async def read_document(args: dict) -> dict:
    """Mock document reader."""
    url = args["url"]
    content = (
        "AWS Lambda durable functions enable long-running, reliable "
        "workflows. Key features include: (1) Automatic state checkpointing "
        "after each step, (2) Configurable retry strategies with exponential "
        "backoff, (3) Wait operations that suspend without compute charges, "
        "(4) Callbacks for human-in-the-loop patterns, (5) Execution "
        "duration up to 1 year, (6) Saga pattern support for compensating "
        "transactions."
    )
    return {"content": [{"type": "text", "text": json.dumps({"content": content, "url": url})}]}


# Bundle tools into an MCP server
research_server = create_sdk_mcp_server(
    name="research",
    tools=[search_web, read_document],
)

RESEARCH_TOOL_NAMES = [
    "mcp__research__search_web",
    "mcp__research__read_document",
]


# ---------------------------------------------------------------------------
# Lambda handler
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a research assistant. When asked a question:
1. Search for relevant information using your tools
2. Read any promising sources for detail
3. Synthesize a clear, concise answer with citations

Be specific — cite sources and include key facts."""


@durable_execution
def handler(event: dict, context: DurableContext) -> dict:
    """Durable Lambda handler — full SDK agent session is checkpointed."""
    prompt = event.get("prompt", "What are AWS Lambda durable functions?")

    context.logger.info("Starting durable agent", extra={"prompt": prompt[:100]})

    result = run_durable_agent(
        context,
        prompt=prompt,
        system=SYSTEM_PROMPT,
        mcp_servers={"research": research_server},
        allowed_tools=RESEARCH_TOOL_NAMES,
        max_turns=5,
    )

    context.logger.info(
        "Agent completed",
        extra={"turns": result["turns"], "cost": result.get("total_cost_usd")},
    )
    return result
