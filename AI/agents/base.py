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
    IS_CLOUD_ENV,
)

logger = logging.getLogger("agent.base")


def _init_llm():
    """Initialize primary LLM: Groq for 24/7 cloud production, or Ollama for local dev."""
    # 1. Use Groq Cloud if provider is 'groq', or if running in cloud, or if GROQ_API_KEY is available
    if LLM_PROVIDER == "groq" or (GROQ_API_KEY and IS_CLOUD_ENV):
        try:
            from agents.groq_llm import get_groq_llm
            logger.info("Initializing Groq Cloud LLM with model: %s", GROQ_MODEL)
            return get_groq_llm()
        except Exception as e:
            logger.warning("Failed to initialize Groq LLM: %s. Attempting fallback.", e)

    # 2. Local Ollama attempt
    if not IS_CLOUD_ENV:
        try:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=MODEL_NAME,
                base_url=OLLAMA_BASE_URL,
                temperature=TEMPERATURE,
            )
        except Exception as e:
            logger.warning("Local Ollama initialization failed: %s", e)

    # 3. Cloud/Fallback to Groq if GROQ_API_KEY is present
    if GROQ_API_KEY:
        try:
            from agents.groq_llm import get_groq_llm
            return get_groq_llm()
        except Exception as e:
            logger.error("Failed to initialize fallback Groq LLM: %s", e)

    # 4. Final fallback to ChatOllama
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
