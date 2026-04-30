"""One-shot script: connect to the Meridian MCP server and dump its tool catalog.

Run: `.venv/bin/python scripts/discover_mcp.py`

Output is to stdout — pipe or copy what you need into the system prompt /
auth-required tool list. Not part of the runtime app.
"""

from __future__ import annotations

import asyncio
import json
import os

from agents.mcp import MCPServerStreamableHttp
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    url = os.environ["MCP_SERVER_URL"]
    print(f"Connecting to {url}\n")

    async with MCPServerStreamableHttp(
        params={"url": url},
        client_session_timeout_seconds=30,
    ) as server:
        tools = await server.list_tools()
        print(f"Found {len(tools)} tools:\n")
        for tool in tools:
            print(f"── {tool.name} " + "─" * (60 - len(tool.name)))
            if tool.description:
                print(f"   {tool.description.strip()}")
            schema = getattr(tool, "inputSchema", None) or {}
            if schema:
                print("   inputSchema:")
                print("   " + json.dumps(schema, indent=2).replace("\n", "\n   "))
            print()


if __name__ == "__main__":
    asyncio.run(main())
