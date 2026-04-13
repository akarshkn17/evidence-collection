# Jira Evidence Automation Platform

Agent-orchestrated evidence collection for Jira tasks with FastAPI, a reusable Jira MCP layer, and optional Playwright screenshot capture.

## Project layout

- `apps/api`: FastAPI interface
- `apps/cli`: CLI interface
- `packages/agent_runtime`: planner + orchestrator
- `packages/jira_mcp`: reusable Jira integration (current MCP tool: `search_issues`)
- `packages/evidence_service`: run folders, exports, summary, manifest
- `packages/browser_automation`: Playwright session and screenshot services
- `output/evidence`: generated run artifacts

## Quickstart (uv)

```bash
uv sync
uv run uvicorn api.main:app --reload --app-dir apps/api/src
```

Run CLI:

```bash
uv run jira-evidence-cli "Get me the list of Jira tickets related to onboarding"
```

Run CLI with screenshots:

```bash
uv run jira-evidence-cli "Get me offboarding jira ticket list" --capture-screenshots
```

## Jira MCP behavior (current)

- Supported operation: `search_issues(jql, max_results, fields)`
- Jira query endpoint: `POST /rest/api/3/search/jql`
- Request is JSON payload based (`jql`, `maxResults`, `fields`)
- Bounded JQL validation is enforced before execution
- Jira API failures preserve response payload in `JiraAPIError.payload`

## Screenshot behavior

- Requires Playwright storage state file (default: `.playwright/storage_state.json`)
- Captures Jira UI list screenshot from JQL-driven issue view
- Captures a rendered records-table screenshot from API results
- If Jira UI screenshot fails due to missing/expired session, non-browser artifacts still complete

## API endpoints

- `GET /health`
- `POST /tasks/jira/search`
- `GET /tasks/{run_id}`

## Environment

Copy `.env.example` to `.env` and populate Jira values.
