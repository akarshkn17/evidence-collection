# Evidence Flow

For each request:

1. Planner creates a `TaskPlan`
2. Orchestrator queries Jira through MCP package
3. Evidence service creates a unique run folder
4. JSON, CSV, summary, samples, and manifest are written
5. Optional Playwright screenshots are captured into `screenshots/`
6. Structured result is returned with artifact paths

Output root defaults to `output/evidence`.

## Screenshot details

When screenshot capture is enabled:

1. Jira UI list screenshot is attempted using Playwright storage state.
2. Rendered table screenshot is created from API records.

Notes:

- Jira UI screenshot requires valid `.playwright/storage_state.json`.
- If Jira UI capture fails, the run still completes with normal evidence artifacts.
- Table screenshot is generated only when records are present.
