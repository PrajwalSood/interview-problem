"""Allowlisted deterministic tool host used by the agent."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Callable, Mapping

from coworker_agent.models import JsonObject, ToolCall


ToolHandler = Callable[[Mapping[str, Any]], Mapping[str, Any]]


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_schema: JsonObject
    handler: ToolHandler

    def as_api_dict(self) -> JsonObject:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }


@dataclass
class ToolRegistry:
    tools: dict[str, Tool]

    def schemas(self) -> list[JsonObject]:
        return [tool.as_api_dict() for tool in self.tools.values()]

    def execute(self, call: ToolCall) -> str:
        """Execute one allowlisted call and always return JSON text.

        Model mistakes become safe tool results so the model may repair them.
        Handler exceptions are bounded and do not expose implementation data.
        """
        tool = self.tools.get(call.name)
        if tool is None:
            return _error("unknown_tool", f"Unknown tool: {call.name}")
        try:
            arguments = json.loads(call.arguments)
        except json.JSONDecodeError:
            return _error("invalid_json", "Tool arguments must be valid JSON")
        if not isinstance(arguments, dict):
            return _error("invalid_arguments", "Tool arguments must be an object")
        validation_error = _validate(arguments, tool.input_schema)
        if validation_error:
            return _error("invalid_arguments", validation_error)
        try:
            result = tool.handler(arguments)
        except Exception:
            return _error("tool_failed", "Tool execution failed")
        return json.dumps({"ok": True, "result": result}, sort_keys=True)


def _error(code: str, message: str) -> str:
    return json.dumps(
        {"ok": False, "error": {"code": code, "message": message}},
        sort_keys=True,
    )


def _validate(arguments: dict[str, Any], schema: JsonObject) -> str | None:
    required = set(schema.get("required", []))
    missing = sorted(required - arguments.keys())
    if missing:
        return "Missing required arguments: " + ", ".join(missing)
    properties = schema.get("properties", {})
    if schema.get("additionalProperties") is False:
        extra = sorted(arguments.keys() - properties.keys())
        if extra:
            return "Unexpected arguments: " + ", ".join(extra)
    expected_types = {
        "string": str,
        "array": list,
        "object": dict,
        "integer": int,
        "boolean": bool,
    }
    for name, value in arguments.items():
        expected_name = properties.get(name, {}).get("type")
        expected_type = expected_types.get(expected_name)
        if expected_type and not isinstance(value, expected_type):
            return f"Argument {name} must be {expected_name}"
    return None
