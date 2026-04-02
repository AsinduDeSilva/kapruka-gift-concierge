from typing import Any
from langchain_openai import OpenAIEmbeddings
from src.infrastructure.config import (
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
    EMBEDDING_SHOW_PROGRESS,
    EMBEDDING_BATCH_SIZE,
    OPENROUTER_BASE_URL,
    get_api_key
)


def get_default_embeddings(
    batch_size: int = EMBEDDING_BATCH_SIZE,
    show_progress: bool = EMBEDDING_SHOW_PROGRESS,
    **kwargs: Any
) -> OpenAIEmbeddings:
    
    llm_kwargs: dict[str, Any] = dict(
        model=EMBEDDING_MODEL,
        show_progress_bar=show_progress,
        **kwargs
    )

    if EMBEDDING_PROVIDER == "openrouter":
        llm_kwargs["openai_api_base"] = OPENROUTER_BASE_URL
        llm_kwargs["openai_api_key"] = get_api_key("openrouter")
    elif EMBEDDING_PROVIDER == "openai":
        llm_kwargs["openai_api_key"] = get_api_key("openai")    

    return OpenAIEmbeddings(**llm_kwargs)




