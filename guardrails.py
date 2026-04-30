from __future__ import annotations

import re

from agent_config import AUTH_REQUIRED_TOOLS

# Patterns that strongly correlate with prompt-injection attempts. We don't try
# to be exhaustive — anything that gets past these is the system prompt's job.
_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"ignore\s+(?:\w+\s+){0,3}previous\s+(?:instructions?|prompts?|messages?)",
        re.I,
    ),
    re.compile(r"disregard\s+(?:\w+\s+){0,3}(?:above|previous|prior)", re.I),
    re.compile(
        r"(?:reveal|show|print|repeat|dump|leak)\s+(?:the\s+)?(?:system|hidden|secret)\s+prompt",
        re.I,
    ),
    re.compile(r"you are now\s+(?!meridian)", re.I),
    re.compile(r"new\s+(?:instructions?|system\s+prompt|persona)", re.I),
    re.compile(r"act as (?:a|an)?\s*(?:dan|jailbreak|admin|root)", re.I),
)

_PIN_PATTERN: re.Pattern[str] = re.compile(r"\b\d{4}\b")


def scrub_input(text: str) -> str:
    """Return `text` with detected prompt-injection phrases neutralized.

    We don't drop the message — that would let an attacker DoS the bot — we
    just rewrite injection markers to `[filtered]` so the model still sees the
    rest of the user's intent.
    """
    cleaned = text
    for pattern in _INJECTION_PATTERNS:
        cleaned = pattern.sub("[filtered]", cleaned)
    return cleaned


def looks_like_injection(text: str) -> bool:
    """True if any injection pattern matches. Used by tests + telemetry."""
    return any(p.search(text) for p in _INJECTION_PATTERNS)


def validate_pin(pin: str) -> bool:
    """Sanity-check a PIN string before sending to the MCP verify tool.

    We do NOT trust this for security — the MCP server is the source of truth.
    This just rejects obvious garbage early.
    """
    return isinstance(pin, str) and bool(re.fullmatch(r"\d{4}", pin))


def requires_auth(tool_name: str) -> bool:
    """True if `tool_name` is account-scoped and needs prior verification."""
    return tool_name in AUTH_REQUIRED_TOOLS


def redact_pin(text: str) -> str:
    """Replace any 4-digit number that looks like a PIN with `****`.

    Used in log lines so PINs never land in stdout / traces / Chainlit output.
    """
    return _PIN_PATTERN.sub("****", text)
