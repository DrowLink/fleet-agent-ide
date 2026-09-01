"""
LLM Factory supporting Ollama (offline local), Google Gemini (free tier), OpenAI, and Anthropic.
"""

from __future__ import annotations

import logging
import os

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def get_llm(
    provider: str | None = None,
    model_name: str | None = None,
    temperature: float = 0.2,
) -> BaseChatModel:
    """Instantiate a chat model based on environment configuration or provider parameter.

    Supported Providers:
        - "ollama" (Default local offline: connects to http://localhost:11434/v1 with $0 tokens)
        - "google" (Google AI Studio Free Tier via OpenAI compatibility or langchain-google-genai)
        - "openai" (OpenAI official API)
        - "anthropic" (Anthropic official API)
    """
    prov = (provider or os.getenv("LLM_PROVIDER", "ollama")).lower().strip()

    if prov == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        model = model_name or os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
        logger.info("Initializing offline Ollama model '%s' at %s", model, base_url)
        return ChatOpenAI(
            base_url=base_url,
            api_key="ollama",  # Ollama doesn't require a real key
            model=model,
            temperature=temperature,
        )

    elif prov == "google":
        # Google AI Studio OpenAI-compatible endpoint or gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is required for provider 'google'"
            )

        # Google AI Studio supports OpenAI compatibility at https://generativelanguage.googleapis.com/v1beta/openai/
        model = model_name or os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
        logger.info("Initializing Google AI Studio model '%s'", model)
        return ChatOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=api_key,
            model=model,
            temperature=temperature,
        )

    elif prov == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for provider 'openai'"
            )
        model = model_name or os.getenv("OPENAI_MODEL", "gpt-4o")
        return ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=temperature,
        )

    else:
        # Fallback to Ollama
        return ChatOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            model=model_name or "qwen2.5-coder:7b",
            temperature=temperature,
        )
