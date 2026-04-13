from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_manifest(
    run_id: str,
    prompt: str,
    artifact_paths: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "prompt": prompt,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": artifact_paths,
        "metadata": metadata or {},
    }


def artifact_relpath(path: Path, root: Path) -> str:
    return str(path.relative_to(root.parent))
