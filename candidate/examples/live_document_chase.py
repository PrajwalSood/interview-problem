from coworker_agent.agent import CoworkerAgent
from coworker_agent.domain import build_document_chase_registry
from coworker_agent.openrouter import OpenRouterClient


def main() -> None:
    agent = CoworkerAgent(
        OpenRouterClient.from_env(),
        build_document_chase_registry(),
    )
    result = agent.run(
        "For FUND-ALPHA and 2026-Q2, determine which expected documents "
        "are missing, create a follow-up draft if necessary, and summarize."
    )
    print(result.final_answer)


if __name__ == "__main__":
    main()
