from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ArtifactPaths(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    run_folder: str
    csv: str | None = None
    json_file: str | None = Field(default=None, alias="json")
    summary: str | None = None
    manifest: str | None = None
    screenshots: list[str] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    status: str
    run_id: str
    summary: str
    sample_records: list[dict[str, Any]]
    artifact_paths: ArtifactPaths
