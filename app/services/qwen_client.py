"""Qwen client through DashScope's OpenAI-compatible endpoint.

Fully configurable: base URL, API key and model come from .env
(app.config.settings). The only inference outside the local machine is
the HTTP call to the LLM API; everything else (orchestration, pgvector,
Docker sandbox) stays local.
"""
from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from ..config import settings


class QwenClient:
    def __init__(self) -> None:
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            if not self.configured:
                raise RuntimeError(
                    "QWEN_API_KEY is not set. Copy .env.example to .env and "
                    "fill in your DashScope key."
                )
            self._client = OpenAI(
                base_url=settings.qwen_base_url,
                api_key=settings.qwen_api_key,
                timeout=30.0,   # evite les appels qui pendent indefiniment
                max_retries=1,
            )
        return self._client

    @property
    def configured(self) -> bool:
        key = settings.qwen_api_key.strip()
        return bool(key) and not key.startswith("sk-your")

    def chat(self, system: str, user: str, temperature: float = 0.4) -> str:
        response = self.client.chat.completions.create(
            model=settings.qwen_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def chat_json(self, system: str, user: str, temperature: float = 0.2) -> dict[str, Any]:
        """Chat expecting a JSON object back; tolerates code fences."""
        raw = self.chat(
            system + "\n\nAnswer ONLY with a valid JSON object. No markdown fences, no commentary.",
            user,
            temperature=temperature,
        )
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
            text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start, end = text.find("{"), text.rfind("}")
            if start != -1 and end > start:
                return json.loads(text[start : end + 1])
            raise


qwen = QwenClient()
