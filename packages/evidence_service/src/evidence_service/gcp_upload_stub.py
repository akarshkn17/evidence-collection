from pathlib import Path
from typing import Protocol


class UploadResult(dict):
    pass


class EvidenceUploader(Protocol):
    def upload_run(self, run_folder: Path, manifest: dict) -> UploadResult: ...


class NoopUploader:
    def upload_run(self, run_folder: Path, manifest: dict) -> UploadResult:
        return UploadResult(
            {
                "status": "skipped",
                "run_folder": str(run_folder),
                "reason": "Uploader not configured",
            }
        )
