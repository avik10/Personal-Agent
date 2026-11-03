"""Base LLM configuration and output sanitization for all agents."""

import re
"""Base LLM configuration and output sanitization for all agents."""

import os
import re
import logging
from config.settings import (
    LLM_PROVIDER,
    MODEL_NAME,
    OLLAMA_BASE_URL,
    TEMPERATURE,
    GROQ_API_KEY,
    GROQ_MODEL,
)

logger = logging.getLogger("agent.base")


def _init_llm():
    """Initialize primary LLM: Groq for 24/7 cloud production, or Ollama for local dev."""
    # If Groq is explicitly chosen or if GROQ_API_KEY is present without Ollama
    if LLM_PROVIDER == "groq" or (GROQ_API_KEY and LLM_PROVIDER != "ollama"):
        try:
            from agents.groq_llm import get_groq_llm
            return get_groq_llm()
        except Exception as e:
            logger.warning("Failed to initialize Groq LLM: %s. Falling back to Ollama.", e)

    # Default to local Ollama
    from langchain_ollama import ChatOllama
    return ChatOllama(
        model=MODEL_NAME,
        base_url=OLLAMA_BASE_URL,
        temperature=TEMPERATURE,
    )


llm = _init_llm()


def clean_agent_output(text: str) -> str:
    """Clean model response, stripping internal thought tags and leaked reasoning blocks."""
    if not text:
        return ""
    if "</think>" in text:
        text = text.split("</think>", 1)[-1]
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"^<think>.*", "", text, flags=re.DOTALL)
    return text.strip()
