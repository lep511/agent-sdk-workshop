"""
Example 2: Human Approval Agent

A Claude agent that generates an action plan, then PAUSES (zero compute cost)
until a human approves or rejects via an external callback. On approval, the
agent executes the plan using MCP tools via the full Claude Agent SDK.

Approval flow:
    1. Invoke the function → agent generates a plan (SDK query, no tools)
    2. Function emits a callback_id (via notify_callback)
    3. Human reviews the plan
    4. Human sends approval:
         aws lambda send-durable-execution-callback-success \
           --callback-id <id> \
           --result '{"approved": true}'
    5. Function resumes → agent executes the plan with full SDK + tools
"""

import json
import sys
from pathlib import Path

from aws_durable_execution_sdk_python import durable_execution, DurableContext
from claude_agent_sdk import tool, create_sdk_mcp_server

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lib.claude_durable import run_durable_agent_with_approval


# ---------------------------------------------------------------------------
# MCP Tools — actions the agent can take AFTER approval
# ---------------------------------------------------------------------------

@tool("send_email", "Send an email to a recipient.", {
    "to": str,
    "subject": str,
    "body": str,
})
async def send_email(args: dict) -> dict:
    """Mock email sender — in production, integrate with SES/SNS."""
    result = {
        "status": "sent",
        "to": args["to"],
        "subject": args["subject"],
        "message_id": "msg-mock-12345",
    }
    return {"content": [{"type": "text", "text": json.dumps(result)}]}


@tool("update_database", "Update a record in the database.", {
    "table": str,
    "record_id": str,
    "updates": dict,
})
async def update_database(args: dict) -> dict:
    """Mock DB update — in production, call DynamoDB/RDS."""
    result = {
        "status": "updated",
        "table": args["table"],
        "record_id": args["record_id"],
        "updates": args["updates"],
    }
    return {"content": [{"type": "text", "text": json.dumps(result)}]}


# Bundle tools into an MCP server
operations_server = create_sdk_mcp_server(
    name="operations",
    tools=[send_email, update_database],
)

OPS_TOOL_NAMES = [
    "mcp__operations__send_email",
    "mcp__operations__update_database",
]


# ---------------------------------------------------------------------------
# Notification callback — tells the human about the pending approval
# ---------------------------------------------------------------------------

def notify_approver(callback_id: str, plan_text: str) -> None:
    """Called when the agent has a plan ready for review.

    In production, this would send a Slack message, email, or post to
    an internal approval dashboard.
    """
    print(f"\n{'='*60}")
    print("APPROVAL REQUIRED")
    print(f"{'='*60}")
    print(f"\nPlan:\n{plan_text}")
    print(f"\nCallback ID: {callback_id}")
    print(f"\nTo approve:")
    print(f"  aws lambda send-durable-execution-callback-success \\")
    print(f"    --callback-id {callback_id} \\")
    print(f"    --result '{{\"approved\": true}}'")
    print(f"\nTo reject:")
    print(f"  aws lambda send-durable-execution-callback-success \\")
    print(f"    --callback-id {callback_id} \\")
    print(f"    --result '{{\"approved\": false, \"reason\": \"Too risky\"}}'")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Lambda handler
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an operations assistant that helps manage customer accounts.
You can send emails and update database records.

Always explain clearly what you're about to do and why.
Be careful with customer communications — get the tone right."""


@durable_execution
def handler(event: dict, context: DurableContext) -> dict:
    """Durable handler with human approval gate using full SDK."""
    prompt = event.get("prompt", "Send a renewal reminder to customer acme-corp")
    timeout_hours = event.get("approval_timeout_hours", 24)

    context.logger.info("Starting approval agent", extra={"prompt": prompt[:100]})

    result = run_durable_agent_with_approval(
        context,
        prompt=prompt,
        system=SYSTEM_PROMPT,
        mcp_servers={"operations": operations_server},
        allowed_tools=OPS_TOOL_NAMES,
        approval_timeout_hours=timeout_hours,
        notify_callback=notify_approver,
    )

    context.logger.info(
        "Agent completed",
        extra={"approved": result.get("approved"), "turns": result.get("turns")},
    )
    return result
