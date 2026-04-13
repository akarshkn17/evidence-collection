import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from agent_runtime.harness_adapter import JiraEvidenceOrchestrator
from agent_runtime.models import OrchestrationInput
from api.schemas.tasks import JiraSearchTaskRequest
from jira_mcp.config import JiraMCPConfig

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _build_orchestrator() -> JiraEvidenceOrchestrator:
    config = JiraMCPConfig()
    evidence_root = Path("output/evidence")
    return JiraEvidenceOrchestrator(
        jira_config=config,
        evidence_root_dir=str(evidence_root),
        playwright_storage_state_path=".playwright/storage_state.json",
    )


@router.post("/jira/search")
def execute_jira_search(request: JiraSearchTaskRequest):
    orchestrator = _build_orchestrator()
    result = orchestrator.execute(
        OrchestrationInput(
            prompt=request.prompt,
            capture_screenshots=request.capture_screenshots,
            export_csv=request.export_csv,
            max_results=request.max_results,
        )
    )
    return result.model_dump(by_alias=True)


@router.get("/{run_id}")
def get_run(run_id: str):
    manifest = Path("output/evidence") / run_id / "manifest.json"
    if not manifest.exists():
        raise HTTPException(status_code=404, detail="Run not found")
    return json.loads(manifest.read_text(encoding="utf-8"))
