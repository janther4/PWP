"""Create tables and seed deterministic mock data for local testing."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from webstore import create_app, db
from webstore.models import Category, Order, Product, Supplier, User

app = create_app()


def _get_or_create_user(email, name):
    user = User.find_by_email(email)
    if user is None:
        user = User(email=email, name=name)
        db.session.add(user)
        db.session.flush()
    return user


def _get_or_create_product(sku, product_name, description, price, stock_quantity):
    product = Product.find_by_sku(sku)
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


def _get_or_create_category(name, description):
    category = Category.find_by_name(name)
    if category is None:
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.flush()
    return category


def _get_or_create_supplier(name, email, phone):
    supplier = Supplier.find_by_name(name)
    if supplier is None:
        supplier = Supplier(name=name, email=email, phone=phone)
        db.session.add(supplier)
        db.session.flush()
    return supplier


def _get_or_create_order(user_id, product_id, quantity, status):
    order = Order.query.filter_by(
        user_id=user_id,
        product_id=product_id,
        quantity=quantity,
        status=status,
    ).first()
    if order is None:
        product = db.session.get(Product, product_id)
        if product is None or product.stock_quantity < quantity:
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

        alice = _get_or_create_user(email="alice@example.com", name="Alice")
        bob = _get_or_create_user(email="bob@example.com", name="Bob")

        keyboard = _get_or_create_product(
            sku="SKU-1001",
            product_name="Mechanical Keyboard",
            description="Hot-swappable 75% keyboard",
            price=119.90,
            stock_quantity=20,
        )
        mouse = _get_or_create_product(
            sku="SKU-1002",
            product_name="Wireless Mouse",
            description="Ergonomic 2.4GHz mouse",
            price=39.90,
            stock_quantity=50,
        )
        _get_or_create_product(
            sku="SKU-1003",
            product_name="USB-C Hub",
            description="7-in-1 USB-C adapter",
            price=54.90,
            stock_quantity=30,
        )

        _get_or_create_category("Electronics", "Electronic devices and accessories")
        _get_or_create_category("Office", "Office products")

        _get_or_create_supplier("North Trade", "north@example.com", "+358401234567")
        _get_or_create_supplier("East Supply", "east@example.com", "+358409998887")

        _get_or_create_order(user_id=alice.id, product_id=keyboard.id, quantity=1, status="placed")
        _get_or_create_order(user_id=bob.id, product_id=mouse.id, quantity=2, status="paid")

        db.session.commit()

        print("Mock data ready.")
        print(f"Users: {User.query.count()}")
        print(f"Products: {Product.query.count()}")
        print(f"Orders: {Order.query.count()}")
        print(f"Categories: {Category.query.count()}")
        print(f"Suppliers: {Supplier.query.count()}")


if __name__ == "__main__":
    seed_mock_data()
