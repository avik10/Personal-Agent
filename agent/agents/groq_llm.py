"""Dedicated Groq Cloud LLM Provider for 24/7 Production Deployment.

Provides high-speed, zero-downtime, serverless LLM inference via Groq Cloud API.
Enables running the multi-agent studio 24/7 in cloud environments (Render, Railway, Fly.io, etc.)
without requiring local hardware or local Ollama daemons.

Supported Production Models on Groq:
- 'llama-3.3-70b-versatile' (Recommended: 128k context, high intelligence & tool calling)
- 'llama-3.1-8b-instant'    (Ultra-low latency, blazing fast)
- 'mixtral-8x7b-32768'      (MoE architecture, 32k context)
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Ensure agent directory is in sys.path when executed directly
_AGENT_DIR = Path(__file__).resolve().parent.parent
if str(_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENT_DIR))

from langchain_groq import ChatGroq

from config.settings import (
    GROQ_API_KEY,
    GROQ_MODEL,
    TEMPERATURE,
)

# Recommended production models available on Groq
GROQ_RECOMMENDED_MODELS: Dict[str, str] = {
    "llama-3.3-70b-versatile": "Default production model: 128k context, state-of-the-art reasoning and tool calling",
    "llama-3.1-8b-instant": "Lightweight model: ultra-fast responses, ideal for low-latency tasks",
    "mixtral-8x7b-32768": "Mixture-of-Experts: 32k context, robust multi-task performance",
}


def get_groq_llm(
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: Optional[float] = None,
    max_retries: int = 2,
) -> ChatGroq:
    """Instantiate and return a configured ChatGroq instance for agents.

    Args:
        model: Groq model identifier (defaults to GROQ_MODEL or 'llama-3.3-70b-versatile').
        api_key: Groq API key (defaults to GROQ_API_KEY from environment/.env).
        temperature: Sampling temperature (defaults to settings.TEMPERATURE).
        max_retries: Number of retries on transient network/rate-limit issues.

    Returns:
        ChatGroq: Configured LangChain chat model ready for agent execution.
    """
    key = (api_key or GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")).strip()
    if not key:
        raise ValueError(
            "GROQ_API_KEY is not set. To use Groq in production, add your free key to .env:\n"
            "  GROQ_API_KEY=gsk_your_key_here\n"
            "Get your free API key at: https://console.groq.com/keys"
        )

    selected_model = (model or GROQ_MODEL or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")).strip()
    temp = temperature if temperature is not None else TEMPERATURE

    return ChatGroq(
        groq_api_key=key,
        model_name=selected_model,
        temperature=temp,
        max_retries=max_retries,
    )


def test_groq_connection(api_key: Optional[str] = None, model: Optional[str] = None) -> bool:
    """Test Groq API connectivity and print diagnostic latency details.

    Useful for verifying production credentials before deployment.
    """
    try:
        print("Testing Groq Cloud LLM connection...")
        client = get_groq_llm(api_key=api_key, model=model)
        start_time = time.time()
        response = client.invoke("Respond with exactly: 'Groq LLM is online and operational.'")
        latency = (time.time() - start_time) * 1000

        print(f"✓ Success! Latency: {latency:.1f}ms")
        print(f"• Model: {client.model_name}")
        print(f"• Response: {response.content.strip()}")
        return True
    except Exception as e:
        print(f"✗ Groq connection failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 65)
    print("  🚀 GROQ CLOUD LLM PRODUCTION ADAPTER TEST")
    print("=" * 65)
    if not (GROQ_API_KEY or os.getenv("GROQ_API_KEY")):
        print("⚠️  GROQ_API_KEY is not set in environment or .env.")
        print("   Set GROQ_API_KEY=gsk_... to test live connection.")
        print(f"   Available models: {list(GROQ_RECOMMENDED_MODELS.keys())}")
    else:
        test_groq_connection()
