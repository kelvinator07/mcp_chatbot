"""End-to-end smoke test: send one short prompt through the agent + MCP and
confirm a trace lands in LangFuse. Run after wiring tracing.

Usage: `python scripts/smoke_langfuse.py`

Requires the live LANGFUSE_* and OPENAI_API_KEY + MCP_SERVER_URL in `.env`.
Costs ~ a fraction of a cent (one gpt-4o-mini call, no tools invoked).
"""
from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

# Import app to trigger _setup_langfuse() at module load.
import app  # noqa: F401, E402
from agents import Agent, Runner  # noqa: E402

from agent_config import MODEL  # noqa: E402


async def main() -> None:
    agent = Agent(
        name="Smoke",
        instructions="Reply with the single word 'pong' and nothing else.",
        model=MODEL,
    )
    result = await Runner.run(agent, input="ping")
    print("agent reply:", result.final_output.strip())
    print(f"check traces at: {os.environ.get('LANGFUSE_HOST', 'https://cloud.langfuse.com')}")


if __name__ == "__main__":
    asyncio.run(main())
