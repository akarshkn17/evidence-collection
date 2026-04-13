from __future__ import annotations

import json

import httpx

from agent_runtime.config import AgentRuntimeConfig


class LLMClient:
    def __init__(self, config: AgentRuntimeConfig):
        self.config = config

    def _endpoint(self) -> str:
        if self.config.agent_llm_provider.lower() == "opencode":
            if self.config.opencode_chat_completions_url:
                return self.config.opencode_chat_completions_url
        if not self.config.llm_base_url:
            raise ValueError("LLM_BASE_URL is required when LLM planner is enabled")
        return self.config.llm_base_url.rstrip("/") + "/chat/completions"

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.config.llm_api_key:
            headers["Authorization"] = f"Bearer {self.config.llm_api_key}"

        payload = {
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        if self.config.llm_model:
            payload["model"] = self.config.llm_model

        with httpx.Client(timeout=float(self.config.llm_timeout_seconds)) as client:
            response = client.post(self._endpoint(), headers=headers, json=payload)

        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        if isinstance(content, list):
            content = "".join(
                chunk.get("text", "") if isinstance(chunk, dict) else str(chunk)
                for chunk in content
            )

        cleaned = str(content).strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()

        return json.loads(cleaned)
