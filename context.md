# Jira MCP Evidence Automation Platform - Project Context

This file is the primary architecture and implementation context for the new Jira evidence automation project.

It should be given to any coding agent, LLM, or developer working on this codebase so they understand the intended design, boundaries, workflows, and non-negotiable implementation rules.

---

## 1. Project Objective

Build a new project that allows a user to request Jira evidence tasks in natural language through an **agent harness**.

Example prompts:
- "Get me the list of Jira tickets related to onboarding"
- "Collect evidence for onboarding and offboarding tickets"
- "Fetch onboarding tickets, export them to CSV, and show me a short summary"

The system must:
1. Accept a natural language task.
2. Use the **agent harness / OpenCode-style orchestration** to interpret intent and plan actions.
3. Query Jira through a **reusable MCP server**.
4. Create a dedicated evidence folder for each run.
5. Store outputs like CSV, JSON, screenshots, summary files, and logs.
6. Return a useful response including:
   - short summary
   - sample records
   - generated file paths
7. Expose the workflow through **FastAPI**
8. Support browser-based evidence screenshots using **Playwright**
9. Be future-ready for uploading evidence to a **GCP bucket**

This should be implemented as a clean new project, not as an incremental patch over the old prototype.

### Current implementation snapshot (this repository)

- Jira MCP currently exposes `search_issues(jql, max_results, fields)`.
- Jira search call is implemented with `POST /rest/api/3/search/jql` and JSON payload.
- Screenshot flow captures both Jira UI list view and rendered table image from API records.
- Jira UI screenshots require valid Playwright storage state (`.playwright/storage_state.json`).
- If Jira UI screenshot capture fails, evidence artifacts (JSON/CSV/summary/manifest) still complete.

---

## 2. High-Level Design Principles

### A. Agent harness is the primary orchestration layer
The project should not be tightly coupled to a direct LLM vendor SDK like OpenRouter.

Instead:
- use the agent harness as the orchestration/runtime layer
- let the agent decide task planning and tool usage
- keep orchestration logic modular and swappable

### B. Jira MCP must be reusable
The Jira MCP component should be generic enough to be shared with other teams.

That means:
- Jira query and API logic should stay reusable
- evidence folder creation should not live inside the core Jira MCP package
- screenshot logic should not live inside the core Jira MCP package
- project-specific workflows should sit above the MCP layer

### C. Evidence automation is separate from Jira access
This project is not just a Jira query client.

It is an evidence collection platform with Jira as the first source system.

### D. FastAPI is required
FastAPI should be a first-class interface, not an afterthought.

### E. Browser automation must respect enterprise auth
Jira uses SSO and MFA.
Do not design the system to bypass these controls.
Use Playwright with interactive login and session reuse.

---

## 3. Required User Experience

For a prompt such as:

`Get me the list of Jira tickets related to onboarding`

The system should:
1. Understand the user request through the agent harness
2. Decide what task steps are needed
3. Query Jira through the MCP tool
4. Create a new evidence folder for that run
5. Export the results to CSV
6. Save structured JSON if useful
7. Generate a short summary
8. Include a few sample records in the response
9. Optionally capture screenshots if configured or requested
10. Return artifact paths for later use

The user should feel like they are using an evidence assistant, not a raw Jira script.

---

## 4. Architecture

The project should be split into five layers.

### Layer 1: Interface Layer
Handles how requests enter the system.

Examples:
- CLI
- FastAPI
- future frontend UI

Responsibilities:
- receive request
- validate input
- call application/orchestration services
- return structured response

### Layer 2: Agent Orchestration Layer
This is the planning layer driven by the agent harness.

Responsibilities:
- understand natural language task
- choose relevant tools/actions
- create a structured task plan
- coordinate downstream steps

Important:
- this layer should not directly call Jira REST endpoints
- it should work through MCP tools or internal service boundaries

### Layer 3: Jira MCP Layer
This is the reusable Jira integration package.

Responsibilities:
- expose Jira tools using MCP
- handle Jira API requests
- normalize Jira results
- remain generic and shareable

### Layer 4: Evidence Service Layer
This is project-specific.

Responsibilities:
- create evidence run folders
- export CSV and JSON
- generate summaries
- store logs
- build manifests
- prepare future upload metadata

### Layer 5: Browser Automation Layer
Handles Playwright-based visual evidence capture.

Responsibilities:
- login/session reuse
- open Jira views
- capture screenshots
- store screenshots in evidence folders

---

## 5. Recommended New Project Structure

```text
jira-evidence-platform/
├── apps/
│   ├── api/
│   │   └── src/api/
│   │       ├── main.py
│   │       ├── routes/
│   │       └── schemas/
│   └── cli/
│       └── src/cli/
│           └── main.py
│
├── packages/
│   ├── jira_mcp/
│   │   └── src/jira_mcp/
│   │       ├── server.py
│   │       ├── jira_api.py
│   │       ├── schemas.py
│   │       ├── config.py
│   │       └── errors.py
│   │
│   ├── agent_runtime/
│   │   └── src/agent_runtime/
│   │       ├── harness_adapter.py
│   │       ├── task_router.py
│   │       ├── planner.py
│   │       ├── models.py
│   │       └── prompt_templates.py
│   │
│   ├── evidence_service/
│   │   └── src/evidence_service/
│   │       ├── run_manager.py
│   │       ├── folder_manager.py
│   │       ├── csv_exporter.py
│   │       ├── json_exporter.py
│   │       ├── summary_builder.py
│   │       ├── manifest_builder.py
│   │       ├── models.py
│   │       └── gcp_upload_stub.py
│   │
│   └── browser_automation/
│       └── src/browser_automation/
│           ├── playwright_session.py
│           ├── jira_login_flow.py
│           ├── jira_views.py
│           ├── screenshot_service.py
│           └── selectors.py
│
├── output/
│   └── evidence/
│
├── docs/
│   ├── architecture.md
│   ├── auth_and_sso.md
│   ├── jira_mcp_contract.md
│   └── evidence_flow.md
│
├── tests/
├── .env.example
├── pyproject.toml
├── uv.lock
└── README.md

---

## 6. Package Management

Use uv as the Python package and environment manager instead of pip.

Requirements:

- manage dependencies through pyproject.toml
- use uv add for dependencies
- use uv run for commands
- keep uv.lock committed
- structure the project cleanly for multi-package development

Do not design this as a loose script folder with ad hoc installs.



## 7. Jira MCP Rules

These are non-negotiable.

### A. Jira search must use POST

When implementing Jira search:

- always use POST-based Jira search requests
- do not rely on GET-based search flows
- do not pass JQL mainly in URL parameters
- send JSON payloads

### B. Preserve bounded query behavior

Jira may reject unbounded or overly broad JQL.
The implementation should preserve safe bounded search behavior.

### C. Preserve error payloads

Do not swallow Jira error bodies.
Return useful diagnostic information.

### D. Keep Jira MCP generic

The Jira MCP layer should expose reusable capabilities such as:

- search issues
- fetch issue details
- possibly later create/update/transition issues

It should not:

- create local evidence folders
- decide report naming
- handle Playwright screenshots
- own GCP upload workflow




## 8. Evidence Run Behavior

Every request execution should create a unique run folder.

Example:

output/evidence/2026-04-11_153045_onboarding_tickets/
├── tickets.csv
├── tickets.json
├── summary.md
├── samples.json
├── screenshots/
│   ├── onboarding_list.png
│   └── offboarding_list.png
├── manifest.json
└── logs.txt

Rules:

never overwrite old runs
folder name should include timestamp + slug
every run should produce a manifest
artifacts should be easy to upload later to GCP


9. Required Outputs

For each successful task, the system should return a structured result containing:

- status
- run id
- short summary
- sample records
- artifact paths

Example shape:

{
  "status": "success",
  "run_id": "2026-04-11_153045_onboarding_tickets",
  "summary": "Found 24 onboarding-related issues. Most are in Open or In Progress.",
  "sample_records": [
    {
      "key": "HR-102",
      "summary": "Employee onboarding checklist",
      "status": "Open"
    },
    {
      "key": "HR-118",
      "summary": "Laptop provisioning for new hire",
      "status": "In Progress"
    }
  ],
  "artifact_paths": {
    "run_folder": "output/evidence/2026-04-11_153045_onboarding_tickets",
    "csv": "output/evidence/2026-04-11_153045_onboarding_tickets/tickets.csv",
    "json": "output/evidence/2026-04-11_153045_onboarding_tickets/tickets.json",
    "summary": "output/evidence/2026-04-11_153045_onboarding_tickets/summary.md",
    "screenshots": [
      "output/evidence/2026-04-11_153045_onboarding_tickets/screenshots/onboarding_list.png"
    ]
  }
}



## 10. FastAPI Requirements

FastAPI should expose the workflow for flexible use by UI or external systems.

Suggested endpoints:

POST /tasks/jira/search

Accepts natural language request and execution flags.

Example:

{
  "prompt": "Get me the list of Jira tickets related to onboarding",
  "capture_screenshots": true,
  "export_csv": true
}
GET /tasks/{run_id}

Returns metadata for a previous run.

GET /health

Basic health endpoint.

Implementation rule:

- API routes should stay thin
- business logic should live in services
- route handlers should call orchestration/application services



## 11. Playwright Screenshot Requirements

A key feature is capturing Jira list screenshots for evidence.

Requirements:

- use Playwright
- navigate Jira issue list/search pages
- capture onboarding and offboarding list screenshots
- store screenshots inside the evidence folder

Enterprise auth constraint

Jira has SSO and MFA.

Do not assume background credential-only login will work.

Preferred approach:

1. first-time interactive login in headful browser
2. user completes SSO/MFA manually
3. save Playwright storage state
4. reuse saved session state in later runs until expired

The design must respect enterprise authentication controls.


## 12. Agent Planning Model

The agent harness should convert user input into a structured task plan instead of relying on fragile free-form text parsing.

Suggested internal model:

from pydantic import BaseModel
from typing import List, Optional

class TaskPlan(BaseModel):
    task_type: str
    user_prompt: str
    search_intent: Optional[str] = None
    jql_hint: Optional[str] = None
    export_csv: bool = True
    capture_screenshots: bool = False
    expected_views: List[str] = []
    max_results: int = 100

The planner should be able to represent actions like:

- query Jira
- summarize results
- export CSV
- capture screenshots

## 13. Security and Secrets

Use environment variables or a proper secrets manager.

Expected config values may include:

- JIRA_BASE_URL
- JIRA_API_TOKEN
- JIRA_EMAIL if needed
- PLAYWRIGHT_STORAGE_STATE_PATH
- EVIDENCE_ROOT_DIR
- GCP_BUCKET_NAME
- GCP_PROJECT_ID

Important:

- Jira API auth and Jira browser login are separate concerns
- API token usage and SSO browser session reuse should be handled separately in code


## 14. Future GCP Upload Provision

Do not prioritize actual GCP upload before the core local flow is working.

But prepare for it now by:

- generating a manifest.json for each run
- storing artifact metadata clearly
- adding an uploader abstraction

Suggested interface:

class EvidenceUploader(Protocol):
    def upload_run(self, run_folder: Path, manifest: dict) -> UploadResult:
        ...

Later, a GCP implementation can be added without changing the rest of the flow.





## 15. Migration Guidance from the Old Prototype

The old prototype had useful ideas, but should not be copied directly.

What to preserve:

- Jira POST request behavior
- lessons learned around GET failures
- flattening/export patterns if still useful
- bounded search logic
- good error handling

What to replace:

- OpenRouter-specific orchestration
- tightly coupled client logic
- single-path CSV-only workflow
- repo structure centered around one prototype client/server pairing


## 16. Non-Negotiable Rules

1. Use a new project structure.
2. Use uv instead of pip.
3. Use the agent harness as the orchestration layer.
4. Keep Jira MCP reusable and generic.
5. Keep evidence logic outside Jira MCP.
6. Use POST for Jira search.
7. Use FastAPI as a first-class interface.
8. Use Playwright for screenshots.
9. Respect SSO and MFA using interactive login/session reuse.
10. Keep the system ready for future GCP evidence upload.


## 17. Final Goal

The final system should become a reusable Jira evidence automation platform built with:

- agent harness orchestration
- reusable MCP integrations
- FastAPI
- Playwright
- structured evidence artifacts
- future cloud archival support

Jira is the first integrated system, but the architecture should make it easy to add other systems later.


## Final recommendation

So, **no**, do not use the old file unchanged.

Use this updated version as your new `context.md`.

If you want, I can next turn this into a more **agent-harness-optimized system prompt** with:
- implementation phases
- coding rules
- done criteria
- folder-by-folder responsibilities
