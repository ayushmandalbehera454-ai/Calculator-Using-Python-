"""Calculator entry point.

    python main.py          -> command-line calculator
    python main.py --gui    -> Tkinter desktop calculator
"""
import sys

from logic import Calculator, CalculatorError

HELP = """Type an expression, e.g.  2 + 3 * (4 - 1)   or   sqrt(16) + 2^3
Functions: sqrt sin cos tan log ln abs   Constants: pi e
Commands : M+  M-  MR  MC  history  clear  help  quit"""


def run_cli() -> None:
    calc = Calculator()
    last = "0"
    print("Python Calculator\n" + HELP)

    while True:
        try:
            text = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            return

        command = text.lower()
        if command in ("quit", "exit", "q"):
            print("Bye!")
            return
        if command == "help":
            print(HELP)
        elif command == "history":
            if not calc.history:
                print("No history yet.")
            for item in calc.history[-10:]:
                print(f"  {item['expression']} = {item['result']}")
        elif command == "clear":
            calc.clear_history()
            print("History cleared.")
        elif command == "mc":
            calc.memory_clear()
            print("Memory cleared.")
        elif command == "mr":
            print("Memory:", calc.memory_recall())
        elif command in ("m+", "m-"):
            try:
                from logic import evaluate
                value = float(evaluate(last))
            except CalculatorError:
                value = 0.0
            (calc.memory_add if command == "m+" else calc.memory_subtract)(value)
            print("Memory:", calc.memory_recall())
        else:
            try:
                last = calc.calculate(text)
                print("=", last)
            except CalculatorError as err:
                print("Error:", err)


def main() -> None:
    if "--gui" in sys.argv:
        from gui import run_gui
        run_gui()
    else:
        run_cli()


if __name__ == "__main__":
    main()
