from __future__ import annotations

from typing import Any

from agent_runtime.config import AgentRuntimeConfig
from agent_runtime.llm_client import LLMClient
from agent_runtime.models import OrchestrationInput, TaskPlan
from agent_runtime.prompt_templates import PLANNER_SYSTEM_PROMPT


class HeuristicTaskPlanner:
    def plan(self, task: OrchestrationInput) -> TaskPlan:
        prompt_lower = task.prompt.lower()

        intent = "onboarding" if "onboarding" in prompt_lower else None
        if "offboarding" in prompt_lower:
            intent = "offboarding" if intent is None else "onboarding offboarding"

        if "onboarding" in prompt_lower and "offboarding" in prompt_lower:
            jql = 'text ~ "onboarding" OR text ~ "offboarding"'
            views = ["onboarding_list", "offboarding_list"]
        elif "onboarding" in prompt_lower:
            jql = 'text ~ "onboarding"'
            views = ["onboarding_list"]
        elif "offboarding" in prompt_lower:
            jql = 'text ~ "offboarding"'
            views = ["offboarding_list"]
        else:
            jql = 'text ~ "' + task.prompt.replace('"', "") + '"'
            views = ["jira_search_results"]

        if "order by" not in jql.lower():
            jql = f"({jql}) ORDER BY created DESC"

        return TaskPlan(
            user_prompt=task.prompt,
            search_intent=intent,
            jql_hint=jql,
            export_csv=task.export_csv,
            capture_screenshots=task.capture_screenshots,
            expected_views=views,
            max_results=task.max_results,
        )


class LLMTaskPlanner:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    @staticmethod
    def _bounded_jql(jql: str) -> str:
        normalized = " ".join(jql.lower().split())
        tokens = [
            "project ",
            "created ",
            "updated ",
            "assignee ",
            "status ",
            "priority ",
            "text ",
            "key ",
            "labels ",
        ]
        if not any(token in normalized for token in tokens):
            return f'(text ~ "{jql.replace(chr(34), "")}") ORDER BY created DESC'
        if "order by" not in normalized:
            return f"({jql}) ORDER BY created DESC"
        return jql

    @staticmethod
    def _bool_or_default(raw: Any, fallback: bool) -> bool:
        if isinstance(raw, bool):
            return raw
        return fallback

    @staticmethod
    def _int_or_default(raw: Any, fallback: int) -> int:
        if isinstance(raw, int) and raw > 0:
            return raw
        return fallback

    @staticmethod
    def _views(raw: Any) -> list[str]:
        if isinstance(raw, list):
            return [str(item) for item in raw if str(item).strip()]
        return ["jira_search_results"]

    def plan(self, task: OrchestrationInput) -> TaskPlan:
        payload = self.llm_client.complete_json(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_prompt=task.prompt,
        )

        raw_jql = str(payload.get("jql") or payload.get("jql_hint") or "")
        jql = self._bounded_jql(raw_jql if raw_jql else task.prompt)

        return TaskPlan(
            user_prompt=task.prompt,
            search_intent=str(payload.get("search_intent") or "").strip() or None,
            jql_hint=jql,
            export_csv=self._bool_or_default(
                payload.get("export_csv"), task.export_csv
            ),
            capture_screenshots=self._bool_or_default(
                payload.get("capture_screenshots"), task.capture_screenshots
            ),
            expected_views=self._views(payload.get("expected_views")),
            max_results=self._int_or_default(
                payload.get("max_results"), task.max_results
            ),
        )


class TaskPlanner:
    def __init__(self, runtime_config: AgentRuntimeConfig | None = None):
        self.runtime_config = runtime_config or AgentRuntimeConfig()
        self.heuristic_planner = HeuristicTaskPlanner()

        self.llm_planner: LLMTaskPlanner | None = None
        can_use_llm = bool(
            self.runtime_config.opencode_chat_completions_url
            or self.runtime_config.llm_base_url
        )
        if self.runtime_config.agent_use_llm_planner and can_use_llm:
            self.llm_planner = LLMTaskPlanner(LLMClient(self.runtime_config))

    def plan(self, task: OrchestrationInput) -> TaskPlan:
        if self.llm_planner is not None:
            try:
                return self.llm_planner.plan(task)
            except Exception:
                return self.heuristic_planner.plan(task)
        return self.heuristic_planner.plan(task)
