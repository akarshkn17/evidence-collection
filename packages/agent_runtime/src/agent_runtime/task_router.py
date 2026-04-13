from agent_runtime.models import TaskPlan


class TaskRouter:
    def route(self, plan: TaskPlan) -> str:
        if plan.task_type == "jira_search":
            return "jira_search_pipeline"
        return "unsupported"
