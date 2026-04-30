"""Tiny pure-function calculator module used as a CI smoke target."""

from __future__ import annotations

from collections.abc import Iterable

Number = int | float


def add(a: Number, b: Number) -> Number:
    return a + b


def subtract(a: Number, b: Number) -> Number:
    return a - b


def multiply(a: Number, b: Number) -> Number:
    return a * b


def divide(a: Number, b: Number) -> float:
    if b == 0:
        raise ZeroDivisionError("cannot divide by zero")
    return a / b


def average(values: Iterable[Number]) -> float:
    items = list(values)
    if not items:
        raise ValueError("average() requires at least one value")
    return sum(items) / len(items)
