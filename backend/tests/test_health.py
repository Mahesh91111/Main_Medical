
def test_liveness_endpoint(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readiness_endpoint_when_database_is_available(
    client,
    monkeypatch,
):
    from app.main import engine

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, statement):
            return 1

    monkeypatch.setattr(
        engine,
        "connect",
        lambda: FakeConnection(),
    )

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_readiness_endpoint_when_database_is_unavailable(
    client,
    monkeypatch,
):
    from app.main import engine

    def fail_connect():
        raise RuntimeError("Synthetic database failure")

    monkeypatch.setattr(engine, "connect", fail_connect)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
