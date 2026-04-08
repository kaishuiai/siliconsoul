from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class LLMClientConfig:
    provider: str = "auto"
    api_base: Optional[str] = None
    model: Optional[str] = None
    timeout_sec: float = 15.0
    temperature: float = 0.2
    max_tokens: int = 800


class LLMClient:
    def __init__(self, config: Optional[LLMClientConfig] = None) -> None:
        self._config = config or LLMClientConfig()

    def is_available(self) -> bool:
        provider = self._resolve_provider()
        if provider == "deepseek":
            return bool(os.getenv("DEEPSEEK_API_KEY", "").strip())
        if provider == "openai_compatible":
            return bool(os.getenv("OPENAI_API_KEY", "").strip())
        return False

    async def chat(
        self,
        *,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout_sec: Optional[float] = None,
        model: Optional[str] = None,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> str:
        provider = self._resolve_provider()
        if provider == "deepseek":
            return await self._chat_deepseek(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_sec=timeout_sec,
                model=model,
                extra_payload=extra_payload,
            )
        if provider == "openai_compatible":
            return await self._chat_openai_compatible(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_sec=timeout_sec,
                model=model,
                extra_payload=extra_payload,
            )
        raise RuntimeError("No LLM provider configured")

    def _resolve_provider(self) -> str:
        provider = (self._config.provider or "auto").strip().lower()
        env_provider = os.getenv("LLM_PROVIDER", "").strip().lower()
        if env_provider == "deepseek" and bool(os.getenv("DEEPSEEK_API_KEY")):
            return "deepseek"
        if env_provider == "openai_compatible" and bool(os.getenv("OPENAI_API_KEY")):
            return "openai_compatible"
        if provider in ("deepseek", "openai_compatible"):
            return provider
        if os.getenv("DEEPSEEK_API_KEY", "").strip():
            return "deepseek"
        if os.getenv("OPENAI_API_KEY", "").strip():
            return "openai_compatible"
        return "none"

    async def _chat_deepseek(
        self,
        *,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        timeout_sec: Optional[float],
        model: Optional[str],
        extra_payload: Optional[Dict[str, Any]],
    ) -> str:
        import aiohttp

        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not set")

        base = (self._config.api_base or "https://api.deepseek.com/v1").rstrip("/")
        url = f"{base}/chat/completions"
        payload: Dict[str, Any] = {
            "model": model or self._config.model or os.getenv("LLM_MODEL", "").strip() or "deepseek-chat",
            "messages": messages,
            "temperature": self._coalesce_float(temperature, self._config.temperature),
            "max_tokens": self._coalesce_int(max_tokens, self._config.max_tokens),
        }
        if extra_payload:
            payload.update(extra_payload)

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        timeout = aiohttp.ClientTimeout(total=self._coalesce_float(timeout_sec, self._config.timeout_sec))

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=timeout) as resp:
                raw = await resp.text()
                if resp.status != 200:
                    raise RuntimeError(f"deepseek http {resp.status}: {raw[:500]}")
                data = json.loads(raw)
                return str(data["choices"][0]["message"]["content"])

    async def _chat_openai_compatible(
        self,
        *,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int],
        timeout_sec: Optional[float],
        model: Optional[str],
        extra_payload: Optional[Dict[str, Any]],
    ) -> str:
        import aiohttp

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        base = (self._config.api_base or os.getenv("LLM_API_BASE", "https://api.openai.com/v1")).rstrip("/")
        url = f"{base}/chat/completions"
        payload: Dict[str, Any] = {
            "model": model or self._config.model or os.getenv("LLM_MODEL", "").strip() or "gpt-3.5-turbo",
            "messages": messages,
            "temperature": self._coalesce_float(temperature, self._config.temperature),
            "max_tokens": self._coalesce_int(max_tokens, self._config.max_tokens),
        }
        if extra_payload:
            payload.update(extra_payload)

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        timeout = aiohttp.ClientTimeout(total=self._coalesce_float(timeout_sec, self._config.timeout_sec))

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=timeout) as resp:
                raw = await resp.text()
                if resp.status != 200:
                    raise RuntimeError(f"openai_compatible http {resp.status}: {raw[:500]}")
                data = json.loads(raw)
                return str(data["choices"][0]["message"]["content"])

    @staticmethod
    def _coalesce_int(value: Optional[int], default: int) -> int:
        if value is None:
            return int(default)
        return int(value)

    @staticmethod
    def _coalesce_float(value: Optional[float], default: float) -> float:
        if value is None:
            return float(default)
        return float(value)
