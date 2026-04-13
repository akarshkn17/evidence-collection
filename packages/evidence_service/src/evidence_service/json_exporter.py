from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def export_json(
    payload: dict[str, Any] | list[dict[str, Any]], output_path: Path
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2, ensure_ascii=False, default=str)
    return output_path
