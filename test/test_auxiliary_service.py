"""Tests for the auxiliary aggregation service."""

from unittest.mock import Mock, patch

import requests
from auxiliary_service import create_aux_app


def _mock_response(payload):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = payload
    return response


def test_summary_aggregates_core_resources():
    app = create_aux_app()

    with patch("auxiliary_service.requests.get") as mock_get:
        mock_get.side_effect = [
            _mock_response({"users": [{"id": 1}, {"id": 2}]}),
            _mock_response(
                {
                    "products": [
                        {"id": 10, "price": 2.5, "stock_quantity": 4},
                        {"id": 11, "price": 10, "stock_quantity": 1},
                    ]
                }
            ),
            _mock_response(
                {
                    "orders": [
                        {"id": 100, "status": "placed"},
                        {"id": 101, "status": "paid"},
                    ]
                }
            ),
        ]

        client = app.test_client()
        response = client.get("/summary/")
        body = response.get_json()

    assert response.status_code == 200
    assert body["counts"] == {"users": 2, "products": 2, "orders": 2, "paid_orders": 1}
    assert body["metrics"]["inventory_value"] == 20.0


def test_summary_returns_502_when_upstream_fails():
    app = create_aux_app()

    with patch("auxiliary_service.requests.get") as mock_get:
        failing = Mock()
        failing.raise_for_status.side_effect = requests.RequestException("boom")
        mock_get.return_value = failing

        client = app.test_client()
        response = client.get("/summary/")
        body = response.get_json()

    assert response.status_code == 502
    assert body["error"] == "upstream_unavailable"
