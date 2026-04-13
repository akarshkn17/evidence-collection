from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentRuntimeConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    agent_use_llm_planner: bool = Field(default=False, alias="AGENT_USE_LLM_PLANNER")
    agent_llm_provider: str = Field(default="opencode", alias="AGENT_LLM_PROVIDER")
    llm_base_url: str | None = Field(default=None, alias="LLM_BASE_URL")
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_model: str | None = Field(default=None, alias="LLM_MODEL")
    llm_timeout_seconds: int = Field(default=45, alias="LLM_TIMEOUT_SECONDS")
    opencode_chat_completions_url: str | None = Field(
        default=None, alias="OPENCODE_CHAT_COMPLETIONS_URL"
    )
