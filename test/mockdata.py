"""Create database tables and seed deterministic mock data for local testing."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app
from models import Order, Product, User, db


def _get_or_create_user(email, name):
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(email=email, name=name)
        db.session.add(user)
        db.session.flush()
    return user


def _get_or_create_product(sku, product_name, description, price, stock_quantity):
    product = Product.query.filter_by(sku=sku).first()
    if product is None:
        product = Product(
            sku=sku,
            product_name=product_name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
        )
        db.session.add(product)
        db.session.flush()
    return product


def _get_or_create_order(user_id, product_id, quantity, status):
    order = Order.query.filter_by(
        user_id=user_id,
        product_id=product_id,
        quantity=quantity,
        status=status,
    ).first()
    if order is None:
        product = db.session.get(Product, product_id)
        if product is None:
            return None
        if product.stock_quantity < quantity:
            return None
        product.stock_quantity -= quantity
        order = Order(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            status=status,
        )
        db.session.add(order)
        db.session.flush()
    return order


def seed_mock_data():
    with app.app_context():
        db.create_all()

        users = [
            {"email": "alice@example.com", "name": "Alice"},
            {"email": "bob@example.com", "name": "Bob"},
        ]

        products = [
            {
                "sku": "SKU-1001",
                "product_name": "Mechanical Keyboard",
                "description": "Hot-swappable 75% keyboard",
                "price": 119.90,
                "stock_quantity": 20,
            },
            {
                "sku": "SKU-1002",
                "product_name": "Wireless Mouse",
                "description": "Ergonomic 2.4GHz mouse",
                "price": 39.90,
                "stock_quantity": 50,
            },
            {
                "sku": "SKU-1003",
                "product_name": "USB-C Hub",
                "description": "7-in-1 USB-C adapter",
                "price": 54.90,
                "stock_quantity": 30,
            },
        ]

        created_users = {}
        created_products = {}

        for item in users:
            user = _get_or_create_user(email=item["email"], name=item["name"])
            created_users[item["email"]] = user

        for item in products:
            product = _get_or_create_product(
                sku=item["sku"],
                product_name=item["product_name"],
                description=item["description"],
                price=item["price"],
                stock_quantity=item["stock_quantity"],
            )
            created_products[item["sku"]] = product

        _get_or_create_order(
            user_id=created_users["alice@example.com"].id,
            product_id=created_products["SKU-1001"].id,
            quantity=1,
            status="placed",
        )
        _get_or_create_order(
            user_id=created_users["bob@example.com"].id,
            product_id=created_products["SKU-1002"].id,
            quantity=2,
            status="paid",
        )

        db.session.commit()

        print("Mock data ready.")
        print(f"Users: {User.query.count()}")
        print(f"Products: {Product.query.count()}")
        print(f"Orders: {Order.query.count()}")


if __name__ == "__main__":
    seed_mock_data()
