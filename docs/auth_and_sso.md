# Auth and SSO

The platform separates API auth from browser auth:

- Jira API token for MCP Jira REST calls
- Playwright interactive login plus storage-state reuse for SSO/MFA protected UI capture

Run an interactive login once by using `PlaywrightSessionManager.ensure_logged_in`, then reuse the saved storage state in future screenshot runs.

## One-time login command

```bash
uv run python -c "from browser_automation.playwright_session import PlaywrightSessionManager; PlaywrightSessionManager('.playwright/storage_state.json').ensure_logged_in('https://your-domain.atlassian.net/issues', '/issues')"
```

## Storage state behavior

- Default storage state path: `.playwright/storage_state.json`
- Jira UI screenshots use this state in headless mode
- If the session expires, rerun interactive login and refresh the file

## Important runtime behavior

- Jira API calls may still succeed even when browser session is expired.
- In that case, JSON/CSV/summary artifacts are still produced, but Jira UI screenshots may fail.
