"""Functional tests for the Webstore REST API.

External libraries used in this test module:
- pytest
- Flask test client (from Flask)
"""

import json
import re

import pytest

from webstore import create_app, db
from webstore.constants import MASON


@pytest.fixture()
def app(tmp_path):
    """Create an isolated Flask app with a temporary SQLite database."""
    database_path = tmp_path / "functional_api_test.db"
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Return a test client for HTTP-level functional tests."""
    return app.test_client()


def _response_json(response):
    return json.loads(response.data)


def _id_from_location(response):
    location = response.headers.get("Location", "")
    match = re.search(r"/(\d+)/?$", location)
    assert match is not None, f"Expected numeric id in Location header, got: {location}"
    return int(match.group(1))


def _create_user(client, email="functional@example.com", name="Functional User"):
    response = client.post("/api/users/", json={"email": email, "name": name})
    assert response.status_code == 201
    return _id_from_location(response)


def _create_product(
    client,
    sku="SKU-FUNC-001",
    product_name="Functional Product",
    price=25.0,
    stock_quantity=10,
):
    response = client.post(
        "/api/products/",
        json={
            "sku": sku,
            "product_name": product_name,
            "description": "Created by functional tests",
            "price": price,
            "stock_quantity": stock_quantity,
        },
    )
    assert response.status_code == 201
    return _id_from_location(response)


# Test case: Verify user creation works and the user appears in the collection response.
def test_user_create_and_list_success(client):
    _create_user(client, email="listcase@example.com", name="List Case")

    response = client.get("/api/users/")
    payload = _response_json(response)

    assert response.status_code == 200
    assert response.mimetype == MASON
    assert isinstance(payload["users"], list)
    assert any(user["email"] == "listcase@example.com" for user in payload["users"])


# Test case: Force an error by sending non-JSON payload to ensure 415 is returned.
def test_user_create_rejects_non_json_payload(client):
    response = client.post("/api/users/", data="not-json", content_type="text/plain")
    payload = _response_json(response)

    assert response.status_code == 415
    assert payload["@error"]["@message"] == "Unsupported media type"


# Test case: Force a conflict by creating two users with the same email to ensure 409 is returned.
def test_user_create_rejects_duplicate_email(client):
    _create_user(client, email="dupe@example.com", name="Original User")

    duplicate = client.post("/api/users/", json={"email": "dupe@example.com", "name": "Other User"})
    payload = _response_json(duplicate)

    assert duplicate.status_code == 409
    assert payload["@error"]["@message"] == "Conflict"


# Test case: Force a schema validation error by sending a negative price to ensure 400 is returned.
def test_product_create_rejects_negative_price(client):
    response = client.post(
        "/api/products/",
        json={
            "sku": "SKU-NEG-001",
            "product_name": "Invalid Product",
            "price": -1.0,
            "stock_quantity": 5,
        },
    )
    payload = _response_json(response)

    assert response.status_code == 400
    assert payload["@error"]["@message"] == "Invalid JSON document"


# Test case: Verify order creation reduces stock and order deletion restores stock.
def test_order_create_and_delete_updates_stock(client):
    user_id = _create_user(client, email="ordercase@example.com", name="Order User")
    product_id = _create_product(client, sku="SKU-STOCK-001", stock_quantity=10)

    create_order = client.post(
        "/api/orders/",
        json={"user_id": user_id, "product_id": product_id, "quantity": 3},
    )
    assert create_order.status_code == 201
    order_id = _id_from_location(create_order)

    product_after_order = client.get(f"/api/products/{product_id}/")
    product_payload_after_order = _response_json(product_after_order)
    assert product_payload_after_order["stock_quantity"] == 7

    delete_order = client.delete(f"/api/orders/{order_id}/")
    assert delete_order.status_code == 204

    product_after_delete = client.get(f"/api/products/{product_id}/")
    product_payload_after_delete = _response_json(product_after_delete)
    assert product_payload_after_delete["stock_quantity"] == 10


# Test case: Force a not-found error by posting an order with a missing user id.
def test_order_create_rejects_missing_user(client):
    product_id = _create_product(client, sku="SKU-MISSING-USER-001", stock_quantity=4)

    response = client.post(
        "/api/orders/",
        json={"user_id": 999999, "product_id": product_id, "quantity": 1},
    )
    payload = _response_json(response)

    assert response.status_code == 404
    assert payload["@error"]["@message"] == "Not found"


# Test case: Force a stock conflict by ordering more units than available.
def test_order_create_rejects_insufficient_stock(client):
    user_id = _create_user(client, email="stockfail@example.com", name="Stock Fail User")
    product_id = _create_product(client, sku="SKU-LOW-STOCK-001", stock_quantity=1)

    response = client.post(
        "/api/orders/",
        json={"user_id": user_id, "product_id": product_id, "quantity": 2},
    )
    payload = _response_json(response)

    assert response.status_code == 409
    assert payload["@error"]["@message"] == "Conflict"


# Test case: Force a validation error in PUT /orders/{id} by omitting required 'status'.
def test_order_put_requires_status_field(client):
    user_id = _create_user(client, email="putcase@example.com", name="Put Case User")
    product_id = _create_product(client, sku="SKU-PUT-001", stock_quantity=5)
    created = client.post(
        "/api/orders/",
        json={"user_id": user_id, "product_id": product_id, "quantity": 1},
    )
    order_id = _id_from_location(created)

    response = client.put(
        f"/api/orders/{order_id}/",
        json={
            "user_id": user_id,
            "product_id": product_id,
            "quantity": 1,
        },
    )
    payload = _response_json(response)

    assert response.status_code == 400
    assert payload["@error"]["@message"] == "Invalid JSON document"
