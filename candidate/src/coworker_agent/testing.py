"""Network-free chat client used by interview tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from coworker_agent.models import (
    AssistantMessage,
    ChatMessage,
    JsonObject,
)


@dataclass
class ScriptedChatClient:
    responses: list[AssistantMessage]
    requests: list[tuple[list[ChatMessage], list[JsonObject]]] = field(
        default_factory=list
    )

    def complete(
        self,
        *,
        messages: Sequence[ChatMessage],
        tools: Sequence[JsonObject],
    ) -> AssistantMessage:
        self.requests.append((list(messages), list(tools)))
        if not self.responses:
            raise AssertionError("Scripted model has no response left")
        return self.responses.pop(0)
