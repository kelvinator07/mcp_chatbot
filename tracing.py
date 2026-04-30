"""LangFuse tracing setup.

One public function: `setup_langfuse()`. Call it once at process start. If
LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are present in the environment,
it wires the openai-agents SDK to a langfuse-instrumented OpenAI client so
every chat-completions call lands as a trace. Otherwise it's a silent no-op.

Why a drop-in client instead of a custom tracing processor: the langfuse
OpenAI integration captures the things you actually need (model, prompt,
response, tokens, latency, cost) with five lines of code. Tool-call spans
within a trace would need an agents.tracing exporter — out of scope for v1.
"""

from __future__ import annotations

import os

from agents import set_default_openai_client


def setup_langfuse() -> bool:
    """Enable LangFuse tracing if credentials are present.

    Returns True iff tracing was wired. Safe to call multiple times.
    """
    if not (os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY")):
        return False

    try:
        from langfuse.openai import AsyncOpenAI as TracedOpenAI
    except ImportError:
        print("[trace] langfuse not installed; skipping", flush=True)
        return False

    set_default_openai_client(TracedOpenAI())
    host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
    print(f"[trace] LangFuse tracing enabled -> {host}", flush=True)
    return True
