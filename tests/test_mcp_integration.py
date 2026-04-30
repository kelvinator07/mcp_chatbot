"""Integration tests against the live Meridian MCP server.

These hit the network, so they're skipped unless `MCP_SERVER_URL` is set.
The CI workflow does NOT set this var, so CI stays hermetic — these run
locally during the build to verify the auth flow really works end-to-end.

Run: `MCP_SERVER_URL=https://order-mcp-...a.run.app/mcp pytest tests/test_mcp_integration.py`
"""

from __future__ import annotations

import os

import pytest
from agents.mcp import MCPServerStreamableHttp
from dotenv import load_dotenv

from agent_config import AUTH_REQUIRED_TOOLS, PUBLIC_TOOLS

load_dotenv()

MCP_URL = os.environ.get("MCP_SERVER_URL")

pytestmark = pytest.mark.skipif(
    not MCP_URL,
    reason="MCP_SERVER_URL not set — skipping live integration tests",
)


@pytest.fixture
async def mcp_server():
    """Open + close the MCP connection for one test."""
    server = MCPServerStreamableHttp(
        params={"url": MCP_URL},
        client_session_timeout_seconds=30,
    )
    await server.connect()
    try:
        yield server
    finally:
        await server.cleanup()


async def test_tool_catalog_matches_expected(mcp_server) -> None:
    """The MCP server exposes the tools we coded against — fail loudly if it drifts."""
    tools = await mcp_server.list_tools()
    names = {t.name for t in tools}
    expected = AUTH_REQUIRED_TOOLS | PUBLIC_TOOLS | {"verify_customer_pin"}
    missing = expected - names
    assert not missing, f"MCP server is missing expected tools: {missing}"


async def test_verify_customer_pin_succeeds_for_valid_credentials(
    mcp_server, valid_customer
) -> None:
    email, pin = valid_customer
    result = await mcp_server.call_tool("verify_customer_pin", {"email": email, "pin": pin})
    text = _extract_text(result)
    # The MCP server returns formatted customer details on success — at minimum
    # the email should appear.
    assert email.lower() in text.lower()


async def test_verify_customer_pin_fails_for_wrong_pin(mcp_server, invalid_customer) -> None:
    email, pin = invalid_customer
    result = await mcp_server.call_tool("verify_customer_pin", {"email": email, "pin": pin})
    text = _extract_text(result).lower()
    # Either the call raises or returns an error string. Both are acceptable;
    # what matters is that the customer's data does NOT come back.
    assert "error" in text or "not found" in text or "incorrect" in text


async def test_list_products_returns_results(mcp_server) -> None:
    """The public browse path must work without authentication."""
    result = await mcp_server.call_tool("list_products", {})
    text = _extract_text(result)
    assert text.strip(), "list_products returned empty content"


def _extract_text(result) -> str:
    """MCP CallToolResult → flattened text. Tolerant of result shape changes."""
    content = getattr(result, "content", None) or []
    parts = []
    for item in content:
        text = getattr(item, "text", None)
        if text:
            parts.append(text)
    return "\n".join(parts) if parts else str(result)
