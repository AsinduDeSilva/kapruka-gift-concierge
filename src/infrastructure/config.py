import os
import yaml
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
from typing import Any, Dict, Optional

load_dotenv()


_PROJECT_ROOT = Path(__file__).parent.parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"


# YAML Config Loading
def _load_yaml(filename: str) -> Dict[str, Any]:
    filepath = _CONFIG_DIR / filename
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _get_nested(d: Dict, *keys, default=None):
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d if d is not None else default


# Load configs  
_PARAMS = _load_yaml("param.yaml")
_MODELS = _load_yaml("models.yaml")


# LLM Defaults
LLM_PROVIDER = _get_nested(_PARAMS, "llm", "provider", default="openrouter")
LLM_TIER = _get_nested(_PARAMS, "llm", "tier", default="general")
LLM_TEMPERATURE = _get_nested(_PARAMS, "llm", "temperature", default=0.0)
LLM_MAX_TOKENS = _get_nested(_PARAMS, "llm", "max_tokens", default=2000)
LLM_STREAMING = _get_nested(_PARAMS, "llm", "streaming", default=False)
OPENROUTER_BASE_URL = _get_nested(_PARAMS, "llm", "openrouter_base_url", default="https://openrouter.ai/api/v1")


# Embedding Defaults
EMBEDDING_PROVIDER = _get_nested(_PARAMS, "embedding", "provider", default="openrouter")
EMBEDDING_TIER = _get_nested(_PARAMS, "embedding", "tier", default="default")
EMBEDDING_BATCH_SIZE = _get_nested(_PARAMS, "embedding", "batch_size", default=100)
EMBEDDING_SHOW_PROGRESS = _get_nested(_PARAMS, "embedding", "show_progress", default=False)


def get_chat_model(provider: Optional[str] = None, tier: Optional[str] = None) -> str:
    provider = provider or LLM_PROVIDER
    tier = tier or LLM_TIER

    return _get_nested(_MODELS, provider, "chat", tier, default="openai/gpt-4o-mini")


def get_embedding_model(provider: Optional[str] = None, tier: Optional[str] = None) -> str:
    provider = provider or EMBEDDING_PROVIDER
    tier = tier or EMBEDDING_TIER

    return _get_nested(_MODELS, provider, "embedding", tier, default="openai/text-embedding-3-small")


CHAT_MODEL = get_chat_model()
EMBEDDING_MODEL = get_embedding_model()

EMBEDDING_DIM = 1536  

if "large" in EMBEDDING_MODEL.lower():
    EMBEDDING_DIM = 3072
elif "small" in EMBEDDING_MODEL.lower() or "ada" in EMBEDDING_MODEL.lower():
    EMBEDDING_DIM = 1536



