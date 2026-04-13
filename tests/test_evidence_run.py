from pathlib import Path

from evidence_service.run_manager import EvidenceRunManager


def test_run_manager_creates_files(tmp_path: Path):
    manager = EvidenceRunManager(tmp_path)
    result = manager.create_run(
        prompt="onboarding tickets",
        records=[{"key": "HR-1", "summary": "Employee onboarding", "status": "Open"}],
        export_csv=True,
    )
    run_folder = Path(result.artifact_paths.run_folder)
    assert run_folder.exists()
    assert (run_folder / "tickets.csv").exists()
    assert (run_folder / "tickets.json").exists()
    assert (run_folder / "manifest.json").exists()
