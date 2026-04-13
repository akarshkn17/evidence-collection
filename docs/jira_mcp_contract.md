# Jira MCP Contract

The Jira MCP package exposes reusable Jira capabilities and avoids project-specific evidence concerns.

## Current supported operation

- `search_issues(jql, max_results=100, fields=None) -> JiraSearchResponse`

## Request and response contract

- Input model: `JiraSearchRequest`
  - `jql: str`
  - `max_results: int`
  - `start_at: int`
  - `fields: list[str]`
- Output model: `JiraSearchResponse`
  - `total: int`
  - `start_at: int`
  - `max_results: int`
  - `issues: list[JiraIssue]`

## API behavior rules

- Jira search uses `POST /rest/api/3/search/jql`
- Request body is JSON (`jql`, `maxResults`, `fields`)
- Unbounded JQL is rejected before Jira call (`JiraQueryValidationError`)
- `max_results` is capped by `JIRA_HARD_MAX_RESULTS`
- Jira error payloads are preserved in `JiraAPIError.payload`

## Explicit non-goals for Jira MCP

- No evidence run folder creation
- No CSV/JSON/report naming decisions
- No Playwright screenshot capture
- No GCP upload orchestration
