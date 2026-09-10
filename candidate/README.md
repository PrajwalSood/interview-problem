# 30-minute exercise: build a private-markets operations agent

Implement a small enterprise coworker that helps an operations analyst chase
quarterly fund documents.

The agent receives a task such as:

> For FUND-ALPHA and 2026-Q2, determine which expected documents are missing,
> create a follow-up draft if necessary, and summarize the result.

It can use four allowlisted tools:

1. `get_fund_profile`
2. `list_expected_documents`
3. `list_received_documents`
4. `create_follow_up_draft`

The last tool creates a **draft**, not a sent email. The agent must never claim
that a message was sent.

## Your task

Implement the two TODOs:

- `OpenRouterClient.complete()` in `src/coworker_agent/openrouter.py`
- `CoworkerAgent.run()` in `src/coworker_agent/agent.py`

Do not use LangChain, PydanticAI, an OpenAI SDK, or another agent framework.
Use the provided models, raw HTTP helper, and tool registry.

Expected implementation size is roughly 50–80 lines.

## Agent loop contract

`CoworkerAgent.run(task)` must:

1. Start with one `system` message and one `user` message.
2. Call `client.complete(messages=..., tools=registry.schemas())`.
3. Append the assistant response to the conversation exactly once.
4. If the assistant requested tools:
   - execute every tool call in order through `registry.execute()`;
   - append one `role="tool"` message per call;
   - preserve its `tool_call_id` and tool name;
   - call the model again with the expanded conversation.
5. If there are no tool calls, return a non-empty final answer.
6. Raise `AgentProtocolError` for an empty final answer.
7. Raise `MaxTurnsExceeded` after `max_turns` model responses without a final
   answer.

Unknown tools, malformed JSON arguments, and invalid argument shapes are
converted by the registry into safe tool-error results. They must be returned
to the model so it can recover; do not execute anything outside the registry.

## Naked OpenRouter API contract

`OpenRouterClient.complete()` must build a request for:

```text
POST https://openrouter.ai/api/v1/chat/completions
model: openai/gpt-5.6-terra
tool_choice: auto
stream: false
```

Use `_post_json()`, which already performs authenticated HTTP. Convert the
first response choice into the provided `AssistantMessage` and `ToolCall`
types. Raise `ModelProtocolError` if the expected response shape is absent or
malformed. Never include the API key in messages, tool results, or exceptions.

## Why this resembles a coding agent

```text
task → LLM decides next step → tool call → deterministic tool execution
     → tool result returned to LLM → repeat → final answer
```

The domain tools replace shell/file tools from a coding agent. The same key
boundary applies: the LLM chooses among advertised tools, but only deterministic
host code executes them.

## Run tests

```bash
python -m pip install -e ".[dev]"
pytest -q
```

The tests do not call OpenRouter.

## Optional live run

After implementing both TODOs:

```bash
export OPENROUTER_API_KEY="..."
python examples/live_document_chase.py
```

The default model is `openai/gpt-5.6-terra`; it can be overridden with
`OPENROUTER_MODEL`.

## Discussion prompts

- How would you persist and resume the loop after a crash?
- How would you keep a tool with external side effects safe?
- How would you prevent prompt injection in document or tool content?
- What should happen when an external action times out ambiguously?
