"""Direct OpenRouter client. No model or agent SDK is used."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from coworker_agent.models import (
    AssistantMessage,
    ChatMessage,
    JsonObject,
    ModelAPIError,
    ModelProtocolError,
)


OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-5.6-terra"


@dataclass
class OpenRouterClient:
    api_key: str
    model: str = DEFAULT_MODEL
    endpoint: str = OPENROUTER_ENDPOINT
    timeout_seconds: float = 30.0

    @classmethod
    def from_env(cls) -> OpenRouterClient:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ModelAPIError("OPENROUTER_API_KEY is not set")
        return cls(
            api_key=api_key,
            model=os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL),
        )

    def complete(
        self,
        *,
        messages: Sequence[ChatMessage],
        tools: Sequence[JsonObject],
    ) -> AssistantMessage:
        """Call OpenRouter and parse its first assistant response.

        TODO: implement the raw request payload and response parsing described
        in the candidate README.
        """
        raise NotImplementedError

    def _post_json(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        """Provided authenticated HTTP transport."""
        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Title": "Enterprise Coworker Agent Interview",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                result = json.loads(response.read())
        except HTTPError as error:
            raise ModelAPIError(
                f"OpenRouter returned HTTP {error.code}"
            ) from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise ModelAPIError("OpenRouter request failed") from error
        if not isinstance(result, Mapping):
            raise ModelProtocolError("OpenRouter response must be an object")
        return result
