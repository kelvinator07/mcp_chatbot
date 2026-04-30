from __future__ import annotations

import os

import chainlit as cl
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent

from agent_config import MODEL, SYSTEM_PROMPT
from guardrails import redact_pin, scrub_input

load_dotenv()

WELCOME = (
    "Hi! I'm **Meridian Support**.\n\n"
    "I can help you:\n"
    "- Browse our products (monitors, keyboards, printers, networking, accessories)\n"
    "- Look up a specific product by SKU\n"
    "- Check your order history (after we verify it's you)\n"
    "- Place a new order\n\n"
    "What can I help you with today?"
)


@cl.on_chat_start
async def on_chat_start() -> None:
    mcp_url = os.environ.get("MCP_SERVER_URL")
    if not mcp_url:
        await cl.Message(content="Configuration error: MCP_SERVER_URL is not set.").send()
        return

    mcp_server = MCPServerStreamableHttp(
        params={"url": mcp_url},
        client_session_timeout_seconds=30,
        cache_tools_list=True,
    )
    await mcp_server.connect()

    agent = Agent(
        name="Meridian Support",
        instructions=SYSTEM_PROMPT,
        model=MODEL,
        mcp_servers=[mcp_server],
    )

    cl.user_session.set("agent", agent)
    cl.user_session.set("mcp_server", mcp_server)
    cl.user_session.set("history", [])

    await cl.Message(content=WELCOME).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    agent: Agent | None = cl.user_session.get("agent")
    if agent is None:
        await cl.Message(content="Session not initialised — please refresh the page.").send()
        return

    raw_user_text = message.content

    # If the user's message contains what looks like a PIN, immediately mask
    # it in the displayed bubble. The agent still gets the original text so
    # verify_customer_pin can authenticate.
    masked = redact_pin(raw_user_text)
    if masked != raw_user_text:
        message.content = masked
        await message.update()

    user_text = scrub_input(raw_user_text)
    history: list = cl.user_session.get("history") or []
    new_input = history + [{"role": "user", "content": user_text}]

    reply = cl.Message(content="")
    await reply.send()

    try:
        result = Runner.run_streamed(agent, input=new_input)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                await reply.stream_token(event.data.delta)

        cl.user_session.set("history", result.to_input_list())
    except Exception as exc:
        # Never leak raw exception text to the user — could include PII or
        # internal details. Log a redacted form, show a friendly message.
        print(f"[agent error] {redact_pin(repr(exc))}", flush=True)
        reply.content = (
            "Sorry, I hit a problem handling that. Could you try rephrasing, "
            "or ask me about products or your order?"
        )

    await reply.update()


@cl.on_chat_end
async def on_chat_end() -> None:
    mcp_server: MCPServerStreamableHttp | None = cl.user_session.get("mcp_server")
    if mcp_server is not None:
        try:
            await mcp_server.cleanup()
        except Exception as exc:
            print(f"[mcp cleanup] {exc!r}", flush=True)
