# Jira Evidence Platform - Detailed Usage Guide

This guide explains how to install, configure, run, and troubleshoot the Jira Evidence Automation Platform.

## 1) What this project does

The platform accepts natural language requests (for example, "get onboarding tickets"), queries Jira through a reusable MCP package, and writes evidence artifacts per run:

- `tickets.csv`
- `tickets.json`
- `summary.md`
- `manifest.json`
- optional screenshots in `screenshots/`

It provides:

- FastAPI interface (`apps/api`)
- CLI interface (`apps/cli`)
- Agent-style orchestration (`packages/agent_runtime`)
- Reusable Jira MCP access layer (`packages/jira_mcp`)
- Evidence artifact service (`packages/evidence_service`)
- Playwright browser capture (`packages/browser_automation`)

Current Jira MCP scope in this codebase:

- `search_issues(jql, max_results, fields)` only

## 2) Prerequisites

- Python `>=3.11`
- `uv` installed
- Jira Cloud URL and API token
- Atlassian account access (for browser screenshots requiring SSO/MFA)

## 3) Initial setup

1. Create environment file:

```bash
copy .env.example .env
```

2. Fill required values in `.env`:

- `JIRA_BASE_URL`
- `JIRA_API_TOKEN`
- `JIRA_EMAIL` (recommended for Jira Cloud API auth)
- `PLAYWRIGHT_STORAGE_STATE_PATH` (default `.playwright/storage_state.json`)
- `EVIDENCE_ROOT_DIR` (default `output/evidence`)

3. Install dependencies and lock:

```bash
uv sync
uv lock
```

4. Install browser binary for screenshots:

```bash
uv run playwright install chromium
```

## 3.1) Enable agentic LLM JQL planning (optional)

By default, the planner uses local heuristics. For complex prompts, enable model-driven JQL generation:

- `AGENT_USE_LLM_PLANNER=true`
- `AGENT_LLM_PROVIDER=opencode`
- `OPENCODE_CHAT_COMPLETIONS_URL` (recommended when using the connected OpenCode provider)
- or `LLM_BASE_URL` (OpenAI-compatible endpoint root, example `https://api.openai.com/v1`)
- `LLM_API_KEY`
- `LLM_MODEL`

Behavior:

1. Orchestrator asks model for a structured task plan and bounded JQL.
2. Returned JQL is normalized (ORDER BY added when missing, bounded fallback applied when unsafe).
3. If model call fails or output is invalid, planner automatically falls back to heuristic planning.

## 4) Authentication model (important)

There are two independent auth paths:

1. **Jira API auth** (used by `jira_mcp` for search)
   - uses API token (+ email basic auth when `JIRA_EMAIL` is present)

2. **Jira browser auth** (used by Playwright screenshots)
   - requires interactive SSO/MFA login once
   - session is saved as Playwright storage state

If browser auth is not completed, Jira UI screenshots can be empty or show no results.

## 5) One-time interactive login for screenshot session

Run this and complete login + MFA in the opened browser window:

```bash
uv run python -c "from browser_automation.playwright_session import PlaywrightSessionManager; PlaywrightSessionManager('.playwright/storage_state.json').ensure_logged_in('https://your-domain.atlassian.net/issues', '/issues')"
```

After successful login, `.playwright/storage_state.json` is created and reused.

## 6) CLI usage

### Basic

```bash
uv run jira-evidence-cli "Get me the list of Jira tickets related to onboarding"
```

### With screenshots

```bash
uv run jira-evidence-cli "Get me offboarding jira ticket list" --capture-screenshots --max-results 100
```

### Options

- `--capture-screenshots`: capture Jira UI + rendered ticket-table screenshot
- `--no-csv`: skip CSV output
- `--max-results <N>`: cap result size
- `--evidence-root <path>`: override output folder
- `--playwright-storage-state <path>`: override storage state file

## 7) API usage

Start server:

```bash
uv run uvicorn api.main:app --reload --app-dir apps/api/src
```

### Health check

`GET /health`

### Execute Jira search task

`POST /tasks/jira/search`

Example request body:

```json
{
  "prompt": "Get me onboarding tickets",
  "capture_screenshots": true,
  "export_csv": true,
  "max_results": 100
}
```

### Fetch run metadata

`GET /tasks/{run_id}`

## 8) Evidence output structure

Each execution creates a unique run folder:

`output/evidence/<timestamp>_<slug>/`

Typical contents:

- `tickets.csv`
- `tickets.json`
- `summary.md`
- `samples.json`
- `manifest.json`
- `screenshots/*.png`

`manifest.json` stores artifact references and metadata for future upload workflows.

## 9) Screenshot behavior

When `--capture-screenshots` is enabled:

1. The system attempts Jira UI screenshot capture via Playwright session state.
2. It also generates a reliable rendered screenshot (`*_tickets_list.png`) from API records.

This dual-capture ensures evidence is still available even if Jira UI filtering behaves unexpectedly.

Current behavior details:

- Jira UI capture requires valid `.playwright/storage_state.json`.
- If Jira UI capture fails because session is missing/expired, run execution still succeeds.
- Rendered table screenshot is created only when at least one record is returned.

## 10) Query safety and Jira behavior

- Jira search is performed via **POST** to `/rest/api/3/search/jql`.
- JQL is validated to avoid fully unbounded searches.
- Jira error response payloads are preserved for diagnostics.

## 11) Running tests

```bash
uv run --extra dev pytest
```

## 12) Troubleshooting

### A) "Jira search failed"

- Verify `.env` values (`JIRA_BASE_URL`, `JIRA_API_TOKEN`, `JIRA_EMAIL`).
- Confirm token permissions in Jira.
- Check if JQL is valid and sufficiently bounded.
- If LLM planner is enabled, verify `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`.
- Temporarily set `AGENT_USE_LLM_PLANNER=false` to validate heuristic fallback behavior.

### B) Blank/empty Jira UI screenshot

- Ensure `.playwright/storage_state.json` exists and is recent.
- Re-run interactive login flow and complete MFA.
- Check if the Jira UI filter itself returns no rows.
- Use the rendered evidence screenshot (`*_tickets_list.png`) to verify fetched records.

### C) No tests found or pytest missing

- Use dev extra explicitly:

```bash
uv run --extra dev pytest
```

## 13) Recommended daily workflow

1. `uv sync`
2. Confirm `.env`
3. If screenshot session expired, re-run interactive login
4. Run CLI/API task
5. Collect artifacts from the new run folder
6. Share `manifest.json` + screenshots as evidence bundle
