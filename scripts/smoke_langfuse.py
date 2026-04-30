"""End-to-end smoke test: send one short prompt through the agent and
confirm a trace lands in LangFuse. Run after wiring tracing.

Usage: `python scripts/smoke_langfuse.py`

Requires the live LANGFUSE_* and OPENAI_API_KEY in `.env`. Costs ~ a
fraction of a cent (one gpt-4o-mini call, no tools invoked).
"""

from __future__ import annotations

import asyncio
import os

from agents import Agent, Runner
from dotenv import load_dotenv

from agent_config import MODEL
from tracing import setup_langfuse

load_dotenv()
setup_langfuse()


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
