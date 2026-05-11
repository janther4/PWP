""" Auxiliary service that aggregates data from the Webstore REST API.  

    Made with github copilot using the prompt create an auxiliary Flask service that collect data from the Webstore REST API 
    and provide a summary endpoint. """


from __future__ import annotations

import os

import requests
from flask import Flask, jsonify


def create_aux_app() -> Flask:
    """Create and configure the auxiliary Flask service."""
    app = Flask(__name__)
    api_base = os.getenv("WEBSTORE_API_BASE", "http://127.0.0.1:5000").rstrip("/")

    def _load(path: str, key: str):
        response = requests.get(f"{api_base}{path}", timeout=5)
        response.raise_for_status()
        return response.json().get(key, [])

    @app.get("/health/")
    def health():
        return {"status": "ok", "service": "webstore-auxiliary"}

    @app.get("/summary/")
    def summary():
        """Return a summary computed from core API resources."""
        try:
            users = _load("/api/users/", "users")
            products = _load("/api/products/", "products")
            orders = _load("/api/orders/", "orders")
        except requests.RequestException as error:
            return jsonify(
                {
                    "error": "upstream_unavailable",
                    "message": str(error),
                }
            ), 502

        inventory_value = sum(
            float(product.get("price", 0)) * int(product.get("stock_quantity", 0))
            for product in products
        )
        paid_orders = sum(1 for order in orders if order.get("status") == "paid")

        return {
            "counts": {
                "users": len(users),
                "products": len(products),
                "orders": len(orders),
                "paid_orders": paid_orders,
            },
            "metrics": {
                "inventory_value": round(inventory_value, 2),
            },
            "source_api_base": api_base,
        }

    return app


app = create_aux_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
