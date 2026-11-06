import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402

client = app.test_client()


def test_home_page():
    assert client.get("/").status_code == 200


def test_health():
    assert client.get("/health").get_json() == {"status": "ok"}


def test_calculate_ok():
    res = client.post("/api/calculate", json={"expression": "2 + 3 * 4"})
    assert res.status_code == 200
    assert res.get_json() == {"result": "14"}


def test_calculate_error():
    res = client.post("/api/calculate", json={"expression": "1 / 0"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_calculate_bad_payload():
    assert client.post("/api/calculate", data="nope").status_code == 400
