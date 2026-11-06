"""Tkinter desktop calculator (runs locally; not used on Render)."""
import tkinter as tk

from logic import Calculator, CalculatorError, evaluate

BG = "#1B2430"
DISPLAY_BG = "#111821"
FG = "#F2F5F8"
BTN_NUM = "#2A3646"
BTN_OP = "#3A4A60"
BTN_EQ = "#2F6FED"
BTN_CLEAR = "#B8433A"

LAYOUT = [
    ["MC", "MR", "M+", "M-"],
    ["C", "⌫", "(", ")"],
    ["7", "8", "9", "÷"],
    ["4", "5", "6", "×"],
    ["1", "2", "3", "-"],
    ["0", ".", "^", "+"],
    ["√", "%", "ANS", "="],
]


class CalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.configure(bg=BG, padx=12, pady=12)
        self.resizable(False, False)

        self.calc = Calculator()
        self.last_answer = "0"
        self.result_text = tk.StringVar()

        self._build_display()
        self._build_buttons()
        self._build_history()

        self.entry.focus_set()
        self.bind("<Return>", lambda _e: self.equals())
        self.bind("<KP_Enter>", lambda _e: self.equals())
        self.bind("<Escape>", lambda _e: self.clear())

    # --- UI ---------------------------------------------------------------
    def _build_display(self):
        self.entry = tk.Entry(
            self, font=("Consolas", 22), justify="right", bg=DISPLAY_BG, fg=FG,
            insertbackground=FG, relief="flat", bd=8,
        )
        self.entry.pack(fill="x")
        tk.Label(
            self, textvariable=self.result_text, font=("Consolas", 14),
            anchor="e", bg=BG, fg="#8FA3BA",
        ).pack(fill="x", pady=(4, 8))

    def _build_buttons(self):
        grid = tk.Frame(self, bg=BG)
        grid.pack()
        for r, row in enumerate(LAYOUT):
            for c, label in enumerate(row):
                color = BTN_NUM
                if label in "÷×-+^%√()":
                    color = BTN_OP
                if label == "=":
                    color = BTN_EQ
                if label in ("C", "MC"):
                    color = BTN_CLEAR if label == "C" else BTN_OP
                tk.Button(
                    grid, text=label, width=5, height=2, font=("Segoe UI", 13),
                    bg=color, fg=FG, activebackground=color, activeforeground=FG,
                    relief="flat", command=lambda t=label: self.on_button(t),
                ).grid(row=r, column=c, padx=3, pady=3)

    def _build_history(self):
        tk.Label(self, text="History (double-click to reuse)", bg=BG, fg="#8FA3BA",
                 anchor="w").pack(fill="x", pady=(10, 2))
        self.history_box = tk.Listbox(
            self, height=5, bg=DISPLAY_BG, fg=FG, relief="flat",
            font=("Consolas", 11), selectbackground=BTN_OP,
        )
        self.history_box.pack(fill="x")
        self.history_box.bind("<Double-Button-1>", self.reuse_history)
        self.refresh_history()

    # --- actions ----------------------------------------------------------
    def on_button(self, label):
        if label == "=":
            self.equals()
        elif label == "C":
            self.clear()
        elif label == "⌫":
            self.entry.delete(len(self.entry.get()) - 1, tk.END)
        elif label == "√":
            self.entry.insert(tk.END, "sqrt(")
        elif label == "ANS":
            self.entry.insert(tk.END, self.last_answer)
        elif label in ("M+", "M-", "MR", "MC"):
            self.memory_action(label)
        else:
            self.entry.insert(tk.END, label)
        self.entry.focus_set()

    def clear(self):
        self.entry.delete(0, tk.END)
        self.result_text.set("")

    def equals(self):
        try:
            self.last_answer = self.calc.calculate(self.entry.get())
        except CalculatorError as err:
            self.result_text.set(f"Error: {err}")
            return
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.last_answer)
        self.result_text.set("")
        self.refresh_history()

    def memory_action(self, label):
        if label == "MC":
            self.calc.memory_clear()
        elif label == "MR":
            self.entry.insert(tk.END, self.calc.memory_recall())
            return
        else:
            try:
                value = float(evaluate(self.entry.get()))
            except CalculatorError as err:
                self.result_text.set(f"Error: {err}")
                return
            (self.calc.memory_add if label == "M+" else self.calc.memory_subtract)(value)
        self.result_text.set(f"Memory: {self.calc.memory_recall()}")

    def refresh_history(self):
        self.history_box.delete(0, tk.END)
        for item in reversed(self.calc.history[-20:]):
            self.history_box.insert(tk.END, f"{item['expression']} = {item['result']}")

    def reuse_history(self, _event):
        selection = self.history_box.curselection()
        if selection:
            item = list(reversed(self.calc.history[-20:]))[selection[0]]
            self.entry.delete(0, tk.END)
            self.entry.insert(0, item["expression"])


def run_gui():
    CalculatorApp().mainloop()


if __name__ == "__main__":
    run_gui()
