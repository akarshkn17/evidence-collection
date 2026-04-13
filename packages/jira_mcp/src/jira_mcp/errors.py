class JiraMCPError(Exception):
    """Base Jira MCP error."""


class JiraQueryValidationError(JiraMCPError):
    """Raised when a Jira search request is invalid or unsafe."""


class JiraAPIError(JiraMCPError):
    """Raised for Jira API failures while preserving server payload."""

    def __init__(self, status_code: int, message: str, payload: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload
