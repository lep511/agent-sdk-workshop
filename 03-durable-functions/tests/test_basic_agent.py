"""
Tests for the durable agent library (Claude Agent SDK integration).

Verifies:
1. run_durable_agent wraps SDK query() in a durable step
2. run_durable_agent_with_approval has plan/wait/execute phases
3. run_multi_agent fans out and synthesizes correctly

Run with:
    cd 03-durable-functions/
    uv run pytest tests/ -v
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.claude_durable import (
    run_durable_agent,
    run_durable_agent_with_approval,
    run_multi_agent,
    _run_sdk_query_sync,
    _step_slug,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_context():
    """Create a mock DurableContext that executes step funcs directly."""
    ctx = MagicMock()
    ctx.logger = MagicMock()

    call_log = []

    def execute_step(func=None, name=""):
        call_log.append(name)
        if func:
            return func(MagicMock())
        return None

    ctx.step = execute_step
    ctx._call_log = call_log
    return ctx


def _mock_sdk_result(text="Done.", turns=1, cost=0.001):
    """Return value simulating what _run_sdk_query_sync would return."""
    return {
        "response": text,
        "turns": turns,
        "total_cost_usd": cost,
        "is_error": False,
        "session_id": "test-session-123",
        "messages": [{"type": "text", "text": text}],
    }


# ---------------------------------------------------------------------------
# Tests: run_durable_agent
# ---------------------------------------------------------------------------

class TestRunDurableAgent:

    @patch("lib.claude_durable._run_sdk_query_sync")
    def test_wraps_query_in_durable_step(self, mock_query):
        """The SDK query is wrapped in a named durable step."""
        mock_query.return_value = _mock_sdk_result("Research complete.")

        ctx = _make_mock_context()
        result = run_durable_agent(
            ctx,
            prompt="What are durable functions?",
            system="You are helpful.",
            mcp_servers={"research": MagicMock()},
            allowed_tools=["mcp__research__search_web"],
        )

        assert result["response"] == "Research complete."
        assert result["turns"] == 1
        assert len(ctx._call_log) == 1
        assert "sdk-agent-" in ctx._call_log[0]

    @patch("lib.claude_durable._run_sdk_query_sync")
    def test_custom_step_name(self, mock_query):
        """Custom step name is used when provided."""
        mock_query.return_value = _mock_sdk_result()

        ctx = _make_mock_context()
        run_durable_agent(ctx, prompt="test", step_name="my-custom-step")

        assert ctx._call_log[0] == "my-custom-step"

    @patch("lib.claude_durable._run_sdk_query_sync")
    def test_task_tool_auto_added_for_agents(self, mock_query):
        """Task tool is automatically added when agents are defined."""
        mock_query.return_value = _mock_sdk_result()
        from claude_agent_sdk import AgentDefinition

        agents = {
            "researcher": AgentDefinition(
                description="Does research",
                prompt="Research things",
            )
        }

        ctx = _make_mock_context()
        run_durable_agent(
            ctx,
            prompt="Delegate to researcher",
            agents=agents,
            allowed_tools=["mcp__research__search"],
        )

        # Verify _run_sdk_query_sync was called with Task in allowed_tools
        call_args = mock_query.call_args
        assert "Task" in call_args.kwargs.get("allowed_tools", call_args[0][3] if len(call_args[0]) > 3 else [])


# ---------------------------------------------------------------------------
# Tests: run_durable_agent_with_approval
# ---------------------------------------------------------------------------

class TestRunDurableAgentWithApproval:

    @patch("lib.claude_durable._run_sdk_query_sync")
    def test_approval_flow_approved(self, mock_query):
        """Full flow: plan → approve → execute."""
        mock_query.side_effect = [
            _mock_sdk_result("## Plan\n1. Send email\n2. Update DB"),
            _mock_sdk_result("Executed: email sent and DB updated."),
        ]

        ctx = _make_mock_context()
        ctx.wait_for_callback = MagicMock(return_value=json.dumps({"approved": True}))

        callback_called = {}

        def track_callback(cb_id, plan):
            callback_called["id"] = cb_id
            callback_called["plan"] = plan

        result = run_durable_agent_with_approval(
            ctx,
            prompt="Send renewal to acme",
            system="Operations assistant",
            mcp_servers={"ops": MagicMock()},
            allowed_tools=["mcp__ops__send_email"],
            notify_callback=track_callback,
        )

        assert result["approved"] is True
        assert "Executed" in result["response"]
        assert "Plan" in result["plan"]
        # Steps: generate-plan + execute-approved-plan
        assert "generate-plan" in ctx._call_log
        assert "execute-approved-plan" in ctx._call_log

    @patch("lib.claude_durable._run_sdk_query_sync")
    def test_approval_flow_rejected(self, mock_query):
        """Rejected plan returns without executing."""
        mock_query.return_value = _mock_sdk_result("## Plan\n1. Something risky")

        ctx = _make_mock_context()
        ctx.wait_for_callback = MagicMock(
            return_value=json.dumps({"approved": False, "reason": "Too risky"})
        )

        result = run_durable_agent_with_approval(
            ctx,
            prompt="Do something",
            system="test",
        )

        assert result["approved"] is False
        assert "Too risky" in result["response"]
        # Only the plan step should have run
        assert "generate-plan" in ctx._call_log
        assert "execute-approved-plan" not in ctx._call_log


# ---------------------------------------------------------------------------
# Tests: run_multi_agent
# ---------------------------------------------------------------------------

class TestRunMultiAgent:

    @patch("lib.claude_durable._run_sdk_query_sync")
    def test_fan_out_and_synthesize(self, mock_query):
        """Multiple sub-agents run, then synthesis produces final briefing."""
        mock_query.side_effect = [
            _mock_sdk_result("Revenue: $4.2B, +18% YoY"),
            _mock_sdk_result("New AI partnership announced"),
            _mock_sdk_result("Strong #2 market position"),
            _mock_sdk_result("Executive briefing: Company is strong."),
        ]

        ctx = _make_mock_context()

        result = run_multi_agent(
            ctx,
            sub_agents={
                "financial": {"prompt": "Analyze financials", "system": "Analyst"},
                "news": {"prompt": "Find news", "system": "Reporter"},
                "competitive": {"prompt": "Assess competition", "system": "Strategist"},
            },
            synthesis_prompt="Combine: {financial} + {news} + {competitive}",
        )

        assert result["total_sub_agents"] == 3
        assert "Revenue" in result["sub_agent_results"]["financial"]
        assert "strong" in result["briefing"].lower()
        # Steps: 3 sub-agents + 1 synthesis
        assert len(ctx._call_log) == 4
        assert "sub-agent-financial" in ctx._call_log
        assert "sub-agent-news" in ctx._call_log
        assert "sub-agent-competitive" in ctx._call_log
        assert "synthesize-results" in ctx._call_log


# ---------------------------------------------------------------------------
# Tests: utility functions
# ---------------------------------------------------------------------------

class TestUtilities:

    def test_step_slug(self):
        """Step slug is short and clean."""
        assert _step_slug("What are durable functions?") == "what-are-durable-functions"
        assert _step_slug("A very long prompt with many words that exceed the limit") == "a-very-long-prompt"
        assert _step_slug("Hello!") == "hello"
