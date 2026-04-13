from __future__ import annotations

from pathlib import Path
from typing import Any

from evidence_service.csv_exporter import export_records_to_csv
from evidence_service.folder_manager import EvidenceFolderManager
from evidence_service.json_exporter import export_json
from evidence_service.manifest_builder import build_manifest
from evidence_service.models import ArtifactPaths, ExecutionResult
from evidence_service.summary_builder import build_summary


class EvidenceRunManager:
    def __init__(self, evidence_root_dir: str | Path):
        self.evidence_root_dir = Path(evidence_root_dir)
        self.folder_manager = EvidenceFolderManager(self.evidence_root_dir)

    def create_run(
        self,
        prompt: str,
        records: list[dict[str, Any]],
        export_csv: bool = True,
        screenshot_paths: list[str] | None = None,
    ) -> ExecutionResult:
        run_id, run_folder = self.folder_manager.create_run_folder(prompt)
        screenshot_paths = screenshot_paths or []

        json_path = run_folder / "tickets.json"
        summary_path = run_folder / "summary.md"
        samples_path = run_folder / "samples.json"
        manifest_path = run_folder / "manifest.json"
        csv_path = run_folder / "tickets.csv"

        export_json(records, json_path)
        export_json(records[:5], samples_path)
        summary_text = build_summary(records, intent=prompt)
        summary_path.write_text(summary_text + "\n", encoding="utf-8")

        csv_rel = None
        if export_csv:
            export_records_to_csv(records, csv_path)
            csv_rel = str(csv_path)

        artifacts = ArtifactPaths(
            run_folder=str(run_folder),
            csv=csv_rel,
            json_file=str(json_path),
            summary=str(summary_path),
            manifest=str(manifest_path),
            screenshots=screenshot_paths,
        )

        manifest = build_manifest(
            run_id=run_id,
            prompt=prompt,
            artifact_paths=artifacts.model_dump(by_alias=True),
            metadata={"record_count": len(records)},
        )
        export_json(manifest, manifest_path)

        return ExecutionResult(
            status="success",
            run_id=run_id,
            summary=summary_text,
            sample_records=records[:5],
            artifact_paths=artifacts,
        )
