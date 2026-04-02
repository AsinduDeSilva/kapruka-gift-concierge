from typing import Optional, Any
from langchain_openai import ChatOpenAI
from src.infrastructure.config import (
    LLM_PROVIDER, 
    CHAT_MODEL, 
    LLM_TEMPERATURE, 
    LLM_MAX_TOKENS, 
    LLM_STREAMING, 
    OPENROUTER_BASE_URL, 
    get_api_key
)

def _build_llm(
    model: str,
    provider: str,
    temperature: float = 0,
    streaming: bool = False,
    max_tokens: Optional[int] = None,
    **kwargs: Any,
) -> ChatOpenAI:

    llm_kwargs: dict[str, Any] = dict(
        model=model,
        temperature=temperature,
        streaming=streaming,
        max_tokens=max_tokens,
        **kwargs,
    )

    if provider == "openrouter":
        llm_kwargs["openai_api_base"] = OPENROUTER_BASE_URL
        llm_kwargs["openai_api_key"] = get_api_key("openrouter")
    elif provider == "openai":
        llm_kwargs["openai_api_key"] = get_api_key("openai")

    return ChatOpenAI(**llm_kwargs)


def get_chat_llm(temperature: float = LLM_TEMPERATURE, **kwargs: Any) -> ChatOpenAI:

    return _build_llm(
        CHAT_MODEL,
        LLM_PROVIDER,
        temperature=temperature,
        max_tokens=LLM_MAX_TOKENS,
        streaming=LLM_STREAMING,
        **kwargs
)