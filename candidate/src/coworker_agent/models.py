"""Complete shared types. Candidates should not need to edit this file."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence


JsonObject = Mapping[str, Any]
ChatMessage = dict[str, Any]


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: str

    def as_api_dict(self) -> ChatMessage:
        return {
            "id": self.id,
            "type": "function",
            "function": {
                "name": self.name,
                "arguments": self.arguments,
            },
        }


@dataclass(frozen=True)
class AssistantMessage:
    content: str | None = None
    tool_calls: tuple[ToolCall, ...] = ()

    def as_api_dict(self) -> ChatMessage:
        message: ChatMessage = {
            "role": "assistant",
            "content": self.content,
        }
        if self.tool_calls:
            message["tool_calls"] = [
                call.as_api_dict() for call in self.tool_calls
            ]
        return message


class ChatClient(Protocol):
    def complete(
        self,
        *,
        messages: Sequence[ChatMessage],
        tools: Sequence[JsonObject],
    ) -> AssistantMessage: ...


@dataclass(frozen=True)
class AgentResult:
    final_answer: str
    messages: tuple[ChatMessage, ...]
    model_turns: int
    tool_invocations: int


class AgentProtocolError(RuntimeError):
    pass


class MaxTurnsExceeded(RuntimeError):
    pass


class ModelAPIError(RuntimeError):
    pass


class ModelProtocolError(RuntimeError):
    pass
