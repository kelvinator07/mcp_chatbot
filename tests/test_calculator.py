import pytest

from calculator import add, average, divide, multiply, subtract


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [(2, 3, 5), (-1, 1, 0), (0, 0, 0), (2.5, 0.5, 3.0)],
)
def test_add(a, b, expected):
    assert add(a, b) == expected


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [(5, 3, 2), (0, 4, -4), (-2, -2, 0)],
)
def test_subtract(a, b, expected):
    assert subtract(a, b) == expected


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [(3, 4, 12), (-2, 5, -10), (0, 99, 0), (1.5, 2, 3.0)],
)
def test_multiply(a, b, expected):
    assert multiply(a, b) == expected


def test_divide_returns_float():
    assert divide(10, 4) == 2.5


def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError, match="cannot divide by zero"):
        divide(1, 0)


def test_average_basic():
    assert average([1, 2, 3, 4]) == 2.5


def test_average_single_value():
    assert average([42]) == 42.0


def test_average_accepts_generator():
    assert average(x for x in [2, 4, 6]) == 4.0


def test_average_empty_raises():
    with pytest.raises(ValueError, match="at least one value"):
        average([])
