import json

from coworker_agent.agent import CoworkerAgent
from coworker_agent.domain import build_document_chase_registry
from coworker_agent.models import AssistantMessage, ToolCall
from coworker_agent.testing import ScriptedChatClient


def test_agent_can_return_a_direct_final_answer() -> None:
    client = ScriptedChatClient(
        [AssistantMessage(content="No action is required.")]
    )
    agent = CoworkerAgent(client, build_document_chase_registry())

    result = agent.run("Summarize the current task.")

    assert result.final_answer == "No action is required."
    assert result.model_turns == 1
    assert result.tool_invocations == 0
    assert result.messages[0]["role"] == "system"
    assert result.messages[1]["role"] == "user"
    assert result.messages[2]["role"] == "assistant"


def test_agent_executes_tool_and_returns_result_to_model() -> None:
    call = ToolCall(
        id="call-1",
        name="get_fund_profile",
        arguments=json.dumps({"fund_code": "FUND-ALPHA"}),
    )
    client = ScriptedChatClient(
        [
            AssistantMessage(tool_calls=(call,)),
            AssistantMessage(content="Alpha Capital is the manager."),
        ]
    )
    agent = CoworkerAgent(client, build_document_chase_registry())

    result = agent.run("Who manages FUND-ALPHA?")

    assert result.model_turns == 2
    assert result.tool_invocations == 1
    assert result.final_answer == "Alpha Capital is the manager."
    second_request_messages = client.requests[1][0]
    assert second_request_messages[-2]["role"] == "assistant"
    assert second_request_messages[-2]["tool_calls"][0]["id"] == "call-1"
    tool_message = second_request_messages[-1]
    assert tool_message["role"] == "tool"
    assert tool_message["tool_call_id"] == "call-1"
    assert tool_message["name"] == "get_fund_profile"
    assert json.loads(tool_message["content"])["ok"] is True


def test_agent_executes_multiple_tool_calls_in_order() -> None:
    calls = (
        ToolCall(
            "expected",
            "list_expected_documents",
            '{"fund_code":"FUND-ALPHA","quarter":"2026-Q2"}',
        ),
        ToolCall(
            "received",
            "list_received_documents",
            '{"fund_code":"FUND-ALPHA","quarter":"2026-Q2"}',
        ),
    )
    client = ScriptedChatClient(
        [
            AssistantMessage(tool_calls=calls),
            AssistantMessage(content="Two documents are missing."),
        ]
    )
    result = CoworkerAgent(
        client, build_document_chase_registry()
    ).run("Check FUND-ALPHA for 2026-Q2.")

    tool_messages = [
        message for message in result.messages if message["role"] == "tool"
    ]
    assert [message["tool_call_id"] for message in tool_messages] == [
        "expected",
        "received",
    ]
    assert result.tool_invocations == 2
