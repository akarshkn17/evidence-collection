from typing import Optional

from pydantic import BaseModel, Field


class TaskPlan(BaseModel):
    task_type: str = "jira_search"
    user_prompt: str
    search_intent: Optional[str] = None
    jql_hint: Optional[str] = None
    export_csv: bool = True
    capture_screenshots: bool = False
    expected_views: list[str] = Field(default_factory=list)
    max_results: int = 100


class OrchestrationInput(BaseModel):
    prompt: str
    capture_screenshots: bool = False
    export_csv: bool = True
    max_results: int = 100
