# Enterprise Coworker Agent — Interview Exercise

Standalone 30-minute Python exercise with no dependency on Brassworks code or
data. The complete candidate problem is in [`candidate/`](candidate/README.md).

The candidate implements a small private-markets operations agent using the
OpenRouter chat-completions API directly—without an agent framework. The agent
uses GPT-5.6 Terra, calls allowlisted document/fund/drafting tools, feeds tool
results back to the model, and stops safely at a bounded final answer.

Tests use a scripted model and mocked HTTP. A live OpenRouter example is
included but is not required for candidate evaluation.
