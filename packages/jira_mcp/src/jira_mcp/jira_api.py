from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

import httpx

from jira_mcp.config import JiraMCPConfig
from jira_mcp.errors import JiraAPIError, JiraQueryValidationError
from jira_mcp.schemas import JiraIssue, JiraSearchRequest, JiraSearchResponse


class JiraAPIClient:
    def __init__(self, config: JiraMCPConfig):
        self.config = config

    def _auth(self) -> tuple[str, str] | None:
        if self.config.jira_email:
            return (self.config.jira_email, self.config.jira_api_token)
        return None

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if not self.config.jira_email:
            headers["Authorization"] = f"Bearer {self.config.jira_api_token}"
        return headers

    def _ensure_bounded(self, jql: str) -> str:
        normalized = " ".join(jql.lower().split())
        bounded_tokens = [
            "project ",
            "created ",
            "updated ",
            "assignee ",
            "status ",
            "priority ",
        ]
        has_bound = any(token in normalized for token in bounded_tokens)
        if not has_bound:
            raise JiraQueryValidationError(
                "JQL appears unbounded. Include at least one scoped clause such as project, status, created, or assignee."
            )
        return jql

    def _cap_max_results(self, requested: int) -> int:
        if requested <= 0:
            return self.config.jira_default_max_results
        return min(requested, self.config.jira_hard_max_results)

    @staticmethod
    def _parse_issue(raw_issue: dict[str, Any]) -> JiraIssue:
        fields = raw_issue.get("fields", {})
        created_raw = fields.get("created")
        created = None
        if created_raw:
            try:
                created = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
            except ValueError:
                created = None

        assignee = fields.get("assignee")
        assignee_name = (
            assignee.get("displayName") if isinstance(assignee, dict) else None
        )
        status = fields.get("status")
        status_name = status.get("name") if isinstance(status, dict) else None

        return JiraIssue(
            key=raw_issue.get("key", ""),
            summary=fields.get("summary"),
            status=status_name,
            assignee=assignee_name,
            created=created,
            raw=raw_issue,
        )

    def search_issues(self, request: JiraSearchRequest) -> JiraSearchResponse:
        jql = self._ensure_bounded(request.jql)
        max_results = self._cap_max_results(request.max_results)
        endpoint = f"{self.config.jira_base_url.rstrip('/')}/rest/api/3/search/jql"

        payload = {
            "jql": jql,
            "maxResults": max_results,
            "fields": request.fields,
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                endpoint, json=payload, headers=self._headers(), auth=self._auth()
            )

        if response.status_code >= 400:
            raise JiraAPIError(
                status_code=response.status_code,
                message="Jira search failed",
                payload=response.text,
            )

        data = response.json()
        raw_issues: Sequence[dict[str, Any]] = data.get("issues", [])
        total = data.get("total")
        start_at = data.get("startAt")
        max_results_resp = data.get("maxResults")

        return JiraSearchResponse(
            total=total if isinstance(total, int) else len(raw_issues),
            start_at=start_at if isinstance(start_at, int) else request.start_at,
            max_results=max_results_resp
            if isinstance(max_results_resp, int)
            else max_results,
            issues=[self._parse_issue(item) for item in raw_issues],
        )
