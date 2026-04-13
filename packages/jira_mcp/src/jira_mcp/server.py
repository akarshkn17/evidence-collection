from jira_mcp.config import JiraMCPConfig
from jira_mcp.jira_api import JiraAPIClient
from jira_mcp.schemas import JiraSearchRequest, JiraSearchResponse


class JiraMCPServer:
    """Reusable MCP-friendly facade for Jira operations."""

    def __init__(self, config: JiraMCPConfig | None = None):
        self.config = config or JiraMCPConfig()
        self.client = JiraAPIClient(self.config)

    def search_issues(
        self, jql: str, max_results: int = 100, fields: list[str] | None = None
    ) -> JiraSearchResponse:
        request = JiraSearchRequest(
            jql=jql,
            max_results=max_results,
            fields=fields or ["summary", "status", "assignee", "created"],
        )
        return self.client.search_issues(request)
