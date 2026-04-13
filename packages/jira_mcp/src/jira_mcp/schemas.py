from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class JiraSearchRequest(BaseModel):
    jql: str
    fields: list[str] = Field(
        default_factory=lambda: ["summary", "status", "assignee", "created"]
    )
    max_results: int = 100
    start_at: int = 0


class JiraIssue(BaseModel):
    key: str
    summary: str | None = None
    status: str | None = None
    assignee: str | None = None
    created: datetime | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class JiraSearchResponse(BaseModel):
    total: int
    start_at: int
    max_results: int
    issues: list[JiraIssue]
