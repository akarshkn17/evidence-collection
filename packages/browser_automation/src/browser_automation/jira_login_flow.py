from browser_automation.playwright_session import PlaywrightSessionManager


def interactive_login(
    session_manager: PlaywrightSessionManager, jira_base_url: str
) -> None:
    session_manager.ensure_logged_in(login_url=jira_base_url)
