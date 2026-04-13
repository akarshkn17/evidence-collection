from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class JiraMCPConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    jira_base_url: str = Field(alias="JIRA_BASE_URL")
    jira_api_token: str = Field(alias="JIRA_API_TOKEN")
    jira_email: str | None = Field(default=None, alias="JIRA_EMAIL")
    jira_default_max_results: int = Field(default=100, alias="JIRA_DEFAULT_MAX_RESULTS")
    jira_hard_max_results: int = Field(default=500, alias="JIRA_HARD_MAX_RESULTS")
