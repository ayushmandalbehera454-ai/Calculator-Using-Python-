"""Flask web app: this is what gets deployed on Render.

The API is stateless. Each visitor's history is kept in their own browser
(localStorage), so people never see each other's calculations.
"""
from flask import Flask, jsonify, render_template, request

from logic import CalculatorError, evaluate, format_number

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/api/calculate")
def calculate():
    data = request.get_json(silent=True) or {}
    expression = data.get("expression", "")
    if not isinstance(expression, str):
        return jsonify(error="Expression must be text"), 400
    try:
        return jsonify(result=format_number(evaluate(expression)))
    except CalculatorError as err:
        return jsonify(error=str(err)), 400


if __name__ == "__main__":
    app.run(debug=True)
