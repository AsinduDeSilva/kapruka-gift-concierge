import os

from typing import Optional

from dotenv import load_dotenv
from loguru import logger
from langfuse import observe as _lf_observe
from langfuse import get_client as _get_lf_client

load_dotenv()

_LANGFUSE_ENABLED = bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))

_client = None

def get_client():
    global _client
    if _client is None:
        _client = _get_lf_client()
    return _client

def observe(
    *,
    name: Optional[str] = None,
    as_type: Optional[str] = None,
):

    def _noop_decorator(fn):
        return fn

    if not _LANGFUSE_ENABLED:
        return _noop_decorator

    kwargs = {}
    if name is not None:
        kwargs["name"] = name
    if as_type is not None:
        kwargs["as_type"] = as_type

    return _lf_observe(**kwargs)


def get_langfuse_callbacks():
    if not _LANGFUSE_ENABLED:
        return []
    try:
        from langfuse.langchain import CallbackHandler
        return [CallbackHandler()]
    except Exception as exc:
        logger.debug("Failed to create Langfuse CallbackHandler: {}", exc)
        return []


def update_current_trace(
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    tags: Optional[list] = None,
) -> None:
    """
    Update the current LangFuse trace with user/session info.

    Safe to call even when tracing is disabled (no-op).
    """
    if not _LANGFUSE_ENABLED:
        return
    try:
        client = get_client()
        kwargs = {}
        if user_id is not None:
            kwargs["user_id"] = user_id
        if session_id is not None:
            kwargs["session_id"] = session_id
        if metadata is not None:
            kwargs["metadata"] = metadata
        if tags is not None:
            kwargs["tags"] = tags
        client.trace(**kwargs)
    except Exception as exc:
        logger.debug("update_current_trace failed (non-critical): {}", exc)


def update_current_observation(
    *,
    input: Optional[str] = None,
    output: Optional[str] = None,
    metadata: Optional[dict] = None,
    usage: Optional[dict] = None,
    model: Optional[str] = None,
) -> None:
    """
    Update the current span/generation with I/O and usage data.

    In LangFuse v3:
    - Generation updates use ``update_current_generation()`` with
      ``model``, ``usage_details``, ``cost_details``.
    - Span updates use ``update_current_span()`` (no model/usage).

    This helper auto-detects which to call based on whether
    ``model`` or ``usage`` are provided.

    Safe to call even when tracing is disabled (no-op).
    """
    if not _LANGFUSE_ENABLED:
        return
    try:
        client = get_client()

        # If model or usage provided → generation update
        if usage is not None or model is not None:
            gen_kwargs = {}
            if input is not None:
                gen_kwargs["input"] = input
            if output is not None:
                gen_kwargs["output"] = output
            if metadata is not None:
                gen_kwargs["metadata"] = metadata
            if model is not None:
                gen_kwargs["model"] = model
            if usage is not None:
                # v3 uses usage_details (input, output, total)
                gen_kwargs["usage_details"] = usage
            try:
                client.update_current_generation(**gen_kwargs)
                return
            except Exception:
                pass

        # Otherwise → span update
        span_kwargs = {}
        if input is not None:
            span_kwargs["input"] = input
        if output is not None:
            span_kwargs["output"] = output
        if metadata is not None:
            span_kwargs["metadata"] = metadata
        if span_kwargs:
            client.update_current_span(**span_kwargs)
    except Exception as exc:
        logger.debug("update_current_observation failed (non-critical): {}", exc)


