from agent_runtime.config import AgentRuntimeConfig
from agent_runtime.models import OrchestrationInput
from agent_runtime.planner import LLMTaskPlanner, TaskPlanner


class _FakeLLMClient:
    def __init__(self, payload: dict):
        self.payload = payload

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        return self.payload


class _RaisingPlanner:
    def plan(self, task: OrchestrationInput):
        raise RuntimeError("planner failed")


def test_llm_task_planner_builds_bounded_jql():
    planner = LLMTaskPlanner(
        _FakeLLMClient(
            {
                "search_intent": "in progress",
                "jql": 'status = "In Progress"',
                "expected_views": ["in_progress_list"],
                "max_results": 200,
            }
        )
    )

    plan = planner.plan(
        OrchestrationInput(prompt="show tickets in progress", max_results=100)
    )

    assert "ORDER BY created DESC" in (plan.jql_hint or "")
    assert plan.max_results == 200
    assert plan.expected_views == ["in_progress_list"]


def test_task_planner_falls_back_when_llm_errors():
    runtime_cfg = AgentRuntimeConfig(
        AGENT_USE_LLM_PLANNER=True,
        OPENCODE_CHAT_COMPLETIONS_URL="https://example.test/chat/completions",
    )
    planner = TaskPlanner(runtime_config=runtime_cfg)
    planner.llm_planner = _RaisingPlanner()

    plan = planner.plan(OrchestrationInput(prompt="Get onboarding tickets"))
    assert "onboarding" in (plan.jql_hint or "")
