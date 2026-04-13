# Project Recreation Context (Build Blueprint)

Use this document as a standalone blueprint to recreate the Jira Evidence Automation Platform from scratch.

## 1) Goal

Build an evidence automation system that:

1. accepts natural-language Jira requests,
2. orchestrates work through an agent-style planning layer,
3. uses a reusable Jira MCP integration package,
4. generates per-run evidence folders and artifacts,
5. supports optional Playwright screenshots with enterprise SSO/MFA,
6. exposes FastAPI and CLI interfaces,
7. remains ready for future GCP evidence upload.

## 2) Non-negotiable architecture rules

1. Keep Jira integration reusable and generic.
2. Keep evidence generation separate from Jira MCP.
3. Use POST-based Jira search (JSON payload).
4. Preserve Jira error payloads for debugging.
5. Use FastAPI as first-class interface.
6. Use Playwright with interactive login + session reuse for SSO/MFA environments.
7. Use `uv` for dependency and environment management.

## 3) Target folder structure

```text
jira-evidence-platform/
├── apps/
│   ├── api/src/api/
│   │   ├── main.py
│   │   ├── routes/
│   │   └── schemas/
│   └── cli/src/cli/
│       └── main.py
├── packages/
│   ├── jira_mcp/src/jira_mcp/
│   │   ├── server.py
│   │   ├── jira_api.py
│   │   ├── schemas.py
│   │   ├── config.py
│   │   └── errors.py
│   ├── agent_runtime/src/agent_runtime/
│   │   ├── harness_adapter.py
│   │   ├── planner.py
│   │   ├── task_router.py
│   │   ├── models.py
│   │   └── prompt_templates.py
│   ├── evidence_service/src/evidence_service/
│   │   ├── run_manager.py
│   │   ├── folder_manager.py
│   │   ├── csv_exporter.py
│   │   ├── json_exporter.py
│   │   ├── summary_builder.py
│   │   ├── manifest_builder.py
│   │   ├── models.py
│   │   └── gcp_upload_stub.py
│   └── browser_automation/src/browser_automation/
│       ├── playwright_session.py
│       ├── jira_login_flow.py
│       ├── jira_views.py
│       ├── screenshot_service.py
│       └── selectors.py
├── output/evidence/
├── docs/
├── tests/
├── .env.example
├── pyproject.toml
└── README.md
```

## 4) Core package responsibilities

### A) `jira_mcp` (reusable integration)

- Own Jira auth/config and API calls.
- Implement `search_issues` using POST `/rest/api/3/search/jql`.
- Keep current MCP scope minimal and stable (search first, expand later).
- Validate bounded JQL.
- Normalize issue fields into typed response models.
- Raise structured errors that include Jira error body.
- Do **not** create evidence folders or screenshots.

### B) `evidence_service` (project-specific evidence logic)

- Create unique run folders (`timestamp + slug`).
- Export CSV/JSON/samples.
- Build short summary and manifest.
- Return structured execution result with artifact paths.
- Include uploader abstraction for future GCP upload.

### C) `browser_automation`

- Manage interactive login and storage-state reuse.
- Capture Jira UI screenshots for configured views.
- Provide fallback reliable screenshot rendering from API records.
- Fail explicitly if storage state is required but missing.
- Keep run execution resilient: evidence artifacts should still be produced when UI capture fails.

### D) `agent_runtime`

- Parse prompt into `TaskPlan`.
- Decide query intent, exports, and screenshot expectations.
- Execute pipeline via MCP + evidence service + browser automation.
- Return standardized run result object.

### E) Interfaces (`apps/api`, `apps/cli`)

- Keep handlers thin.
- Build orchestration input from request/args.
- Call orchestrator.
- Return structured response.

## 5) Data contract for execution result

```json
{
  "status": "success",
  "run_id": "2026-04-13_120000_onboarding_tickets",
  "summary": "Found N Jira issues ...",
  "sample_records": [
    {"key": "KAN-1", "summary": "...", "status": "To Do"}
  ],
  "artifact_paths": {
    "run_folder": "output/evidence/...",
    "csv": "output/evidence/.../tickets.csv",
    "json": "output/evidence/.../tickets.json",
    "summary": "output/evidence/.../summary.md",
    "manifest": "output/evidence/.../manifest.json",
    "screenshots": ["output/evidence/.../screenshots/file.png"]
  }
}
```

## 6) Config surface (`.env`)

Expected keys:

- `JIRA_BASE_URL`
- `JIRA_API_TOKEN`
- `JIRA_EMAIL`
- `JIRA_DEFAULT_MAX_RESULTS`
- `JIRA_HARD_MAX_RESULTS`
- `PLAYWRIGHT_STORAGE_STATE_PATH`
- `EVIDENCE_ROOT_DIR`
- `AGENT_USE_LLM_PLANNER`
- `AGENT_LLM_PROVIDER`
- `OPENCODE_CHAT_COMPLETIONS_URL`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `GCP_BUCKET_NAME`
- `GCP_PROJECT_ID`

## 7) Build steps from zero

1. Initialize `pyproject.toml` with package paths and scripts.
2. Add required dependencies (`fastapi`, `httpx`, `pydantic`, `pydantic-settings`, `playwright`, `uvicorn`, etc.).
3. Build package skeletons and `__init__.py` files.
4. Implement Jira client and schemas.
5. Implement evidence managers and exporters.
6. Implement browser session + screenshot services.
7. Implement planner + orchestrator.
8. Wire API routes and CLI command.
9. Add tests for planner and run manager.
10. Create docs and `.env.example`.
11. Run `uv lock`, `uv run --extra dev pytest`, and a real CLI smoke test.

## 8) Operational behavior to preserve

1. Never overwrite previous run folders.
2. Always produce `manifest.json` per run.
3. Keep screenshot artifacts inside each run's `screenshots/`.
4. Preserve Jira diagnostic payloads on API failure.
5. Respect enterprise auth constraints (SSO/MFA).

## 9) Known implementation lessons

1. Jira endpoint migration matters (`/search/jql` vs old `/search`).
2. Browser session state is mandatory for reliable Jira UI screenshots.
3. UI filters can diverge from API JQL expectations; capture a rendered table screenshot from API records as a reliability fallback.
4. Keep orchestration adaptable so future data sources can be added without rewriting Jira MCP.

## 10) Done criteria for recreation

Project is complete when:

1. CLI can execute natural language Jira requests and output artifact paths.
2. API endpoint `POST /tasks/jira/search` works end-to-end.
3. Each run creates evidence files + manifest in a unique folder.
4. Jira query uses POST and bounded search logic.
5. Playwright screenshot flow supports interactive login and session reuse.
6. Tests pass with `uv run --extra dev pytest`.
