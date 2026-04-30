"""Shared test fixtures.

Test customer credentials live here, never at the repo root.
"""

from __future__ import annotations

import pytest

# Real test customers from the assessment data set. Live in the repo only here,
# inside `tests/`, which the deployment Dockerfile excludes from the runtime
# image (tests aren't shipped).
TEST_CUSTOMERS: list[tuple[str, str]] = [
    ("donaldgarcia@example.net", "7912"),
    ("michellejames@example.com", "1520"),
    ("laurahenderson@example.org", "1488"),
    ("spenceamanda@example.org", "2535"),
    ("glee@example.net", "4582"),
    ("williamsthomas@example.net", "4811"),
    ("justin78@example.net", "9279"),
    ("jason31@example.com", "1434"),
    ("samuel81@example.com", "4257"),
    ("williamleon@example.net", "9928"),
]


@pytest.fixture
def valid_customer() -> tuple[str, str]:
    """First test customer — known-good credentials."""
    return TEST_CUSTOMERS[0]


@pytest.fixture
def invalid_customer() -> tuple[str, str]:
    """Email that exists in the dataset, but with a wrong PIN."""
    email, _ = TEST_CUSTOMERS[0]
    return (email, "0000")


@pytest.fixture
def unknown_customer() -> tuple[str, str]:
    """An email that doesn't exist in the system at all."""
    return ("nobody@example.com", "0000")
