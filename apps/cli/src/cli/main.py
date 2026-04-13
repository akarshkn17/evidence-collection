import argparse
import json

from agent_runtime.harness_adapter import JiraEvidenceOrchestrator
from agent_runtime.models import OrchestrationInput
from jira_mcp.config import JiraMCPConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Jira evidence automation CLI")
    parser.add_argument("prompt", help="Natural language task prompt")
    parser.add_argument("--capture-screenshots", action="store_true")
    parser.add_argument("--no-csv", action="store_true", help="Skip CSV export")
    parser.add_argument("--max-results", type=int, default=100)
    parser.add_argument("--evidence-root", default="output/evidence")
    parser.add_argument(
        "--playwright-storage-state", default=".playwright/storage_state.json"
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    orchestrator = JiraEvidenceOrchestrator(
        jira_config=JiraMCPConfig(),
        evidence_root_dir=args.evidence_root,
        playwright_storage_state_path=args.playwright_storage_state,
    )
    result = orchestrator.execute(
        OrchestrationInput(
            prompt=args.prompt,
            capture_screenshots=args.capture_screenshots,
            export_csv=not args.no_csv,
            max_results=args.max_results,
        )
    )
    print(json.dumps(result.model_dump(by_alias=True), indent=2, default=str))


if __name__ == "__main__":
    main()
