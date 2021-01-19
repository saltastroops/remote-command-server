import pytest
from fastapi.testclient import TestClient

from saao_deployment_server.main import app


client = TestClient(app)


def test_route_not_found():
    """Calling a non-existing route gives a 404 error."""
    response = client.get("/uyxfvgisd")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"projectt": "whatever", "version": "1.0.8"},
        {"project": "whatever", "versio": "1.2.9"},
        {"project": "whatever", "version": "7.8.1", "extra": 98},
        {"project": "whatever"},
        {"version": "9.67.5"},
    ],
)
def test_invalid_request_body(body):
    """Invalid request bodies lead to a 400 error."""
    response = client.post("/deploy", json=body)
    assert response.status_code == 123
