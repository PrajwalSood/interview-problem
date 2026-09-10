from typing import Any, Mapping

from coworker_agent.models import ToolCall
from coworker_agent.openrouter import OpenRouterClient


class RecordingClient(OpenRouterClient):
    def __init__(self, response: Mapping[str, Any]) -> None:
        super().__init__(api_key="not-used")
        self.response = response
        self.payload: Mapping[str, Any] | None = None

    def _post_json(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        self.payload = payload
        return self.response


def test_openrouter_client_builds_payload_and_parses_tool_calls() -> None:
    response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "type": "function",
                            "function": {
                                "name": "get_fund_profile",
                                "arguments": '{"fund_code":"FUND-ALPHA"}',
                            },
                        }
                    ],
                }
            }
        ]
    }
    client = RecordingClient(response)
    tools = [{"type": "function", "function": {"name": "example"}}]

    result = client.complete(
        messages=[{"role": "user", "content": "hello"}],
        tools=tools,
    )

    assert client.payload is not None
    assert client.payload["model"] == "openai/gpt-5.6-terra"
    assert client.payload["tool_choice"] == "auto"
    assert client.payload["stream"] is False
    assert client.payload["messages"][0]["content"] == "hello"
    assert client.payload["tools"] == tools
    assert result.content is None
    assert result.tool_calls == (
        ToolCall(
            "call-1",
            "get_fund_profile",
            '{"fund_code":"FUND-ALPHA"}',
        ),
    )
