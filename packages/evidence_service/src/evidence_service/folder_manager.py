from __future__ import annotations

from datetime import datetime
from pathlib import Path

from slugify import slugify


class EvidenceFolderManager:
    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)

    def create_run_folder(self, prompt: str) -> tuple[str, Path]:
        self.root_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        prompt_slug = slugify(prompt)[:50] or "jira_task"
        run_id = f"{timestamp}_{prompt_slug}"
        run_folder = self.root_dir / run_id
        run_folder.mkdir(parents=True, exist_ok=False)
        (run_folder / "screenshots").mkdir(parents=True, exist_ok=True)
        return run_id, run_folder
