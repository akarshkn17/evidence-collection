# Architecture

This platform implements a five-layer architecture:

1. Interface layer (`apps/api`, `apps/cli`)
2. Agent orchestration layer (`packages/agent_runtime`)
3. Jira MCP layer (`packages/jira_mcp`)
4. Evidence service layer (`packages/evidence_service`)
5. Browser automation layer (`packages/browser_automation`)

## Current execution path

1. API or CLI receives a natural-language prompt.
2. Planner builds a `TaskPlan` with JQL hint, flags, and limits.
3. Orchestrator calls Jira MCP (`JiraMCPServer.search_issues`).
4. Evidence service writes run artifacts (`tickets.json`, `tickets.csv`, `summary.md`, `samples.json`, `manifest.json`).
5. If screenshots are enabled, browser automation captures Jira UI list screenshot and rendered table screenshot.

## Layer boundaries

- `jira_mcp` owns Jira auth, POST search calls, validation, and normalized responses.
- `evidence_service` owns run folders and artifact generation.
- `browser_automation` owns Playwright login/session reuse and screenshot capture.
- `agent_runtime` coordinates all layers but does not call Jira REST directly.

## Current MCP scope

The Jira MCP layer currently exposes one operation: `search_issues(jql, max_results, fields)`.
