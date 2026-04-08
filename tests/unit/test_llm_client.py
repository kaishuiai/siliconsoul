import pytest

from src.llm.client import LLMClient, LLMClientConfig


def test_llm_client_provider_resolution(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    llm = LLMClient(LLMClientConfig(provider="auto"))
    assert llm.is_available() is False

    monkeypatch.setenv("DEEPSEEK_API_KEY", "x")
    llm2 = LLMClient(LLMClientConfig(provider="auto"))
    assert llm2.is_available() is True

    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "y")
    llm3 = LLMClient(LLMClientConfig(provider="auto"))
    assert llm3.is_available() is True


@pytest.mark.asyncio
async def test_llm_client_chat_raises_when_key_missing(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    llm = LLMClient(LLMClientConfig(provider="openai_compatible"))
    with pytest.raises(RuntimeError):
        await llm.chat(messages=[{"role": "user", "content": "hi"}], max_tokens=1)

    llm2 = LLMClient(LLMClientConfig(provider="deepseek"))
    with pytest.raises(RuntimeError):
        await llm2.chat(messages=[{"role": "user", "content": "hi"}], max_tokens=1)


@pytest.mark.asyncio
async def test_llm_client_chat_raises_when_no_provider(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    llm = LLMClient(LLMClientConfig(provider="auto"))
    with pytest.raises(RuntimeError):
        await llm.chat(messages=[{"role": "user", "content": "hi"}], max_tokens=1)
