"""Tests for GET /health.

Sanity check that the app boots and CORS-free GET works. Runs as the
"hello world" canary — if this fails, the app is broken at the import
level."""


def test_health_returns_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert "version" in body
