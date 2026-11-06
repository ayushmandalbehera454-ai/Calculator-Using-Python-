import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic import Calculator, CalculatorError, evaluate, format_number  # noqa: E402


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("2 + 3", 5),
        ("10 - 4", 6),
        ("6 * 7", 42),
        ("8 / 2", 4),
        ("2 + 3 * (4 - 1)", 11),
        ("2 ^ 3", 8),
        ("2 ** 3", 8),
        ("17 // 5", 3),
        ("17 % 5", 2),
        ("-5 + 2", -3),
        ("sqrt(16)", 4),
        ("6 × 7 ÷ 2", 21),
        ("abs(-3)", 3),
    ],
)
def test_valid_expressions(expression, expected):
    assert evaluate(expression) == pytest.approx(expected)


def test_constants_and_functions():
    assert evaluate("pi") == pytest.approx(3.14159265)
    assert evaluate("log(1000)") == pytest.approx(3)
    assert evaluate("ln(e)") == pytest.approx(1)


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "   ",
        "1 / 0",
        "5 % 0",
        "2 +",
        "abc",
        "sqrt(-1)",
        "(-8) ** 0.5",
        "2 ** 100000",
        "__import__('os').system('echo hi')",
        "open('x')",
        "'a' + 'b'",
        "1" * 300,
    ],
)
def test_invalid_or_unsafe_expressions(expression):
    with pytest.raises(CalculatorError):
        evaluate(expression)


def test_format_number():
    assert format_number(5.0) == "5"
    assert format_number(0.1 + 0.2) == "0.3"
    assert format_number(2.5) == "2.5"


def test_history_and_memory(tmp_path):
    path = tmp_path / "history.json"
    calc = Calculator(history_file=path)
    assert calc.calculate("2 + 2") == "4"
    assert json.loads(path.read_text())[0] == {"expression": "2 + 2", "result": "4"}

    calc.memory_add(5)
    calc.memory_subtract(2)
    assert calc.memory_recall() == "3"
    calc.memory_clear()
    assert calc.memory_recall() == "0"

    calc.clear_history()
    assert calc.history == []


def test_history_persists(tmp_path):
    path = tmp_path / "history.json"
    Calculator(history_file=path).calculate("1 + 1")
    assert len(Calculator(history_file=path).history) == 1
