from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_runtime.models import OrchestrationInput
from agent_runtime.planner import TaskPlanner
from browser_automation.screenshot_service import JiraScreenshotService
from evidence_service.models import ExecutionResult
from evidence_service.run_manager import EvidenceRunManager
from jira_mcp.config import JiraMCPConfig
from jira_mcp.server import JiraMCPServer


class JiraEvidenceOrchestrator:
    def __init__(
        self,
        jira_config: JiraMCPConfig,
        evidence_root_dir: str,
        playwright_storage_state_path: str,
    ):
        self.jira_server = JiraMCPServer(jira_config)
        self.run_manager = EvidenceRunManager(evidence_root_dir)
        self.planner = TaskPlanner()
        self.screenshot_service = JiraScreenshotService(
            jira_base_url=jira_config.jira_base_url,
            storage_state_path=playwright_storage_state_path,
        )

    @staticmethod
    def _to_records(issues: list[Any]) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for issue in issues:
            records.append(
                {
                    "key": issue.key,
                    "summary": issue.summary,
                    "status": issue.status,
                    "assignee": issue.assignee,
                    "created": issue.created.isoformat() if issue.created else None,
                }
            )
        return records

    def execute(self, task_input: OrchestrationInput) -> ExecutionResult:
        plan = self.planner.plan(task_input)

        response = self.jira_server.search_issues(
            jql=plan.jql_hint or "ORDER BY created DESC",
            max_results=plan.max_results,
        )
        records = self._to_records(response.issues)

        run = self.run_manager.create_run(
            prompt=task_input.prompt,
            records=records,
            export_csv=plan.export_csv,
            screenshot_paths=[],
        )

        if plan.capture_screenshots:
            prompt_lower = task_input.prompt.lower()
            default_view_name = "jira_list"
            if "onboarding" in prompt_lower:
                default_view_name = "onboarding_list"
            elif "offboarding" in prompt_lower:
                default_view_name = "offboarding_list"

            issue_keys = [record.get("key") for record in records if record.get("key")]
            views = []
            if issue_keys:
                keys = ", ".join(issue_keys[:50])
                views.append(
                    (default_view_name, f"key in ({keys}) ORDER BY created DESC")
                )
            else:
                views.append(
                    (default_view_name, plan.jql_hint or "ORDER BY created DESC")
                )

            screenshot_paths: list[str] = []
            try:
                screenshot_paths.extend(
                    self.screenshot_service.capture_issue_views(
                        run_folder=Path(run.artifact_paths.run_folder),
                        views=views,
                    )
                )
            except RuntimeError:
                pass

            if records:
                table_name = "jira_tickets_list"
                table_title = "Jira Ticket List"
                if "onboarding" in prompt_lower:
                    table_name = "onboarding_tickets_list"
                    table_title = "Onboarding Jira Ticket List"
                elif "offboarding" in prompt_lower:
                    table_name = "offboarding_tickets_list"
                    table_title = "Offboarding Jira Ticket List"

                table_shot = self.screenshot_service.capture_records_table(
                    run_folder=Path(run.artifact_paths.run_folder),
                    name=table_name,
                    records=records,
                    title=table_title,
                )
                screenshot_paths.append(table_shot)

            run.artifact_paths.screenshots = screenshot_paths

        return run
