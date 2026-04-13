from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from browser_automation.jira_views import issue_search_url
from browser_automation.playwright_session import PlaywrightSessionManager


class JiraScreenshotService:
    def __init__(self, jira_base_url: str, storage_state_path: str):
        self.jira_base_url = jira_base_url
        self.session_manager = PlaywrightSessionManager(storage_state_path)

    def capture_issue_views(
        self, run_folder: str | Path, views: list[tuple[str, str]]
    ) -> list[str]:
        from playwright.sync_api import TimeoutError, sync_playwright

        run_folder = Path(run_folder)
        screenshots_dir = run_folder / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        paths: list[str] = []

        if not self.session_manager.storage_state_path.exists():
            raise RuntimeError(
                "Playwright storage state not found. Run an interactive Jira login first to save SSO/MFA session state."
            )

        with sync_playwright() as pw:
            browser, context = self.session_manager.get_browser_context(
                playwright=pw, headless=True
            )
            page = context.new_page()
            for name, jql in views:
                url = issue_search_url(self.jira_base_url, jql)
                page.goto(url, wait_until="domcontentloaded", timeout=90000)
                try:
                    page.get_by_role("button", name="Accept all").click(timeout=4000)
                except TimeoutError:
                    pass
                page.wait_for_timeout(6000)

                shot_path = screenshots_dir / f"{name}.png"
                page.screenshot(path=str(shot_path), full_page=True)
                paths.append(str(shot_path))
            context.close()
            browser.close()

        return paths

    def capture_records_table(
        self,
        run_folder: str | Path,
        name: str,
        records: list[dict[str, Any]],
        title: str,
    ) -> str:
        from playwright.sync_api import sync_playwright

        run_folder = Path(run_folder)
        screenshots_dir = run_folder / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        html_path = screenshots_dir / f"{name}.html"
        screenshot_path = screenshots_dir / f"{name}.png"

        rows = []
        for record in records:
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(record.get('key', '')))}</td>"
                f"<td>{html.escape(str(record.get('summary', '')))}</td>"
                f"<td>{html.escape(str(record.get('status', '')))}</td>"
                "</tr>"
            )

        html_content = (
            "<!doctype html><html><head><meta charset='utf-8'><title>Evidence</title>"
            "<style>body{font-family:Segoe UI,Arial,sans-serif;padding:24px;background:#f7f8fa;color:#172b4d;}"
            "h1{margin:0 0 12px;font-size:22px;}table{border-collapse:collapse;width:100%;background:#fff;}"
            "th,td{border:1px solid #dfe1e6;padding:10px;text-align:left;vertical-align:top;}"
            "th{background:#f4f5f7;} .meta{color:#5e6c84;margin-bottom:16px;}</style></head><body>"
            f"<h1>{html.escape(title)}</h1>"
            f"<div class='meta'>Generated from Jira API results. Total records: {len(records)}</div>"
            "<table><thead><tr><th>Key</th><th>Summary</th><th>Status</th></tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table></body></html>"
        )
        html_path.write_text(html_content, encoding="utf-8")

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1600, "height": 1000})
            page.goto(html_path.resolve().as_uri(), wait_until="domcontentloaded")
            page.wait_for_timeout(600)
            page.screenshot(path=str(screenshot_path), full_page=True)
            browser.close()

        return str(screenshot_path)
