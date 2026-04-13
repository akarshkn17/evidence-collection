from agent_runtime.models import OrchestrationInput
from agent_runtime.planner import TaskPlanner


def test_planner_onboarding_defaults():
    planner = TaskPlanner()
    plan = planner.plan(OrchestrationInput(prompt="Get onboarding tickets"))
    assert "onboarding" in (plan.jql_hint or "")
    assert plan.export_csv is True
