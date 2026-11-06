"""Core calculator logic: safe expression evaluation, memory and history.

This module has no GUI or web dependencies, so the same code powers the
command-line, Tkinter and Flask (web) versions of the calculator.
"""
import ast
import json
import math
import operator
from pathlib import Path

HISTORY_FILE = Path(__file__).parent / "history.json"
MAX_EXPRESSION_LENGTH = 200
MAX_EXPONENT = 1000


class CalculatorError(Exception):
    """Raised for any user-facing calculation problem."""


_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log10,
    "ln": math.log,
    "abs": abs,
}
_CONSTANTS = {"pi": math.pi, "e": math.e}


def _normalize(expression: str) -> str:
    """Convert display symbols into valid Python operators."""
    return (
        expression.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("^", "**")
    )


def _eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise CalculatorError("Only numbers are allowed")

    if isinstance(node, ast.Name):
        if node.id in _CONSTANTS:
            return _CONSTANTS[node.id]
        raise CalculatorError(f"Unknown name: {node.id}")

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow):
            if abs(right) > MAX_EXPONENT:
                raise CalculatorError("Exponent is too large")
            result = float(left) ** right  # float avoids huge integers
            if isinstance(result, complex):
                raise CalculatorError("Result is not a real number")
            return result
        return _BINARY_OPS[type(node.op)](left, right)

    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _FUNCTIONS
        and not node.keywords
        and len(node.args) == 1
    ):
        return _FUNCTIONS[node.func.id](_eval(node.args[0]))

    raise CalculatorError("Invalid expression")


def evaluate(expression: str):
    """Safely evaluate a math expression like '2 + 3 * (4 - 1)'."""
    if not expression or not expression.strip():
        raise CalculatorError("Enter an expression")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise CalculatorError("Expression is too long")

    try:
        tree = ast.parse(_normalize(expression.strip()), mode="eval")
    except (SyntaxError, ValueError):
        raise CalculatorError("Invalid expression") from None

    try:
        return _eval(tree.body)
    except ZeroDivisionError:
        raise CalculatorError("Cannot divide by zero") from None
    except OverflowError:
        raise CalculatorError("Number is too large") from None
    except ValueError:
        raise CalculatorError("Math domain error") from None
    except RecursionError:
        raise CalculatorError("Expression is too complex") from None


def format_number(value) -> str:
    """Show whole numbers without '.0' and trim float noise."""
    if isinstance(value, float):
        if value.is_integer() and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.10g}"
    return str(value)


def load_history(path=HISTORY_FILE) -> list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def save_history(history: list, path=HISTORY_FILE) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except OSError:
        pass  # history is a convenience; never crash because of it


class Calculator:
    """Calculator with memory (M+, M-, MR, MC) and persistent history."""

    def __init__(self, history_file=HISTORY_FILE, max_history=100):
        self.history_file = history_file
        self.max_history = max_history
        self.memory = 0.0
        self.history = load_history(history_file)

    def calculate(self, expression: str) -> str:
        result = format_number(evaluate(expression))
        self.history.append({"expression": expression.strip(), "result": result})
        self.history = self.history[-self.max_history:]
        save_history(self.history, self.history_file)
        return result

    # --- memory -----------------------------------------------------------
    def memory_add(self, value: float) -> None:
        self.memory += value

    def memory_subtract(self, value: float) -> None:
        self.memory -= value

    def memory_recall(self) -> str:
        return format_number(self.memory)

    def memory_clear(self) -> None:
        self.memory = 0.0

    # --- history ----------------------------------------------------------
    def clear_history(self) -> None:
        self.history = []
        save_history(self.history, self.history_file)
