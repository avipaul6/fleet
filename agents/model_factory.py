"""Resolve a config string into an ADK-compatible model.

Plain Gemini id     -> pass string straight to ADK (native path).
Prefixed id         -> wrap in LiteLlm so any Vertex Model Garden model works,
                       e.g. "vertex_ai/claude-sonnet-4-5". Swap models per agent
                       tier with env vars; no code changes.
"""
from config.settings import settings

_LITELLM_PREFIXES = ("vertex_ai/", "litellm/", "openai/", "anthropic/")


def resolve(model_id: str):
    if model_id.startswith(_LITELLM_PREFIXES):
        from google.adk.models.lite_llm import LiteLlm
        return LiteLlm(model=model_id.removeprefix("litellm/"))
    return model_id  # native Gemini string


def fast():
    return resolve(settings.model_fast)


def strong():
    return resolve(settings.model_strong)
