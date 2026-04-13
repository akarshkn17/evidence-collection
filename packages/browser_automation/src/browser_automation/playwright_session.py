from __future__ import annotations

from pathlib import Path


class PlaywrightSessionManager:
    def __init__(self, storage_state_path: str | Path):
        self.storage_state_path = Path(storage_state_path)

    def ensure_logged_in(
        self, login_url: str, done_url_contains: str | None = None
    ) -> None:
        from playwright.sync_api import sync_playwright

        self.storage_state_path.parent.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto(login_url)
            if done_url_contains:
                page.wait_for_url(f"**{done_url_contains}**", timeout=180000)
            else:
                page.wait_for_timeout(60000)
            context.storage_state(path=str(self.storage_state_path))
            browser.close()

    def get_browser_context(self, playwright, headless: bool = True):
        browser = playwright.chromium.launch(headless=headless)
        if self.storage_state_path.exists():
            context = browser.new_context(storage_state=str(self.storage_state_path))
        else:
            context = browser.new_context()
        return browser, context
