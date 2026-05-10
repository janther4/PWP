"""Database models for the webstore API."""

import click
from flask.cli import with_appcontext

from webstore import db


class ModelAccessMixin:
    """Small access helper mixin for model queries and persistence."""

    @classmethod
    def get_all(cls):
        """Return all rows ordered by primary key."""
        return cls.query.order_by(cls.id).all()

    @classmethod
    def get_by_id(cls, row_id):
        """Return one row by primary key or None."""
        return db.session.get(cls, row_id)

    def save(self):
        """Persist this model instance."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete this model instance."""
        db.session.delete(self)
        db.session.commit()


class User(ModelAccessMixin, db.Model):
    """Customer user model."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Text, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))

    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")

    def serialize(self):
        """Return user data as a dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at,
        }

    def deserialize(self, data):
        """Update user data from a dictionary."""
        self.email = data["email"]
        self.name = data["name"]

    @classmethod
    def find_by_email(cls, email):
        """Return a user by email or None."""
        return cls.query.filter_by(email=email).first()

    @staticmethod
    def json_schema():
        """JSON schema for user data."""
        return {
            "type": "object",
            "properties": {
                "email": {"type": "string", "minLength": 1},
                "name": {"type": "string", "minLength": 1},
            },
            "required": ["email", "name"],
            "additionalProperties": False,
        }


class Product(ModelAccessMixin, db.Model):
    """Product model."""

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sku = db.Column(db.Text, nullable=False, unique=True)
    product_name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    created_at = db.Column(db.Text, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))

    orders = db.relationship("Order", back_populates="product")

    __table_args__ = (
        db.CheckConstraint("price >= 0", name="price_non_negative"),
        db.CheckConstraint("stock_quantity >= 0", name="stock_non_negative"),
    )

    def serialize(self):
        """Return product data as a dictionary."""
        return {
            "id": self.id,
            "sku": self.sku,
            "product_name": self.product_name,
            "description": self.description,
            "price": self.price,
            "stock_quantity": self.stock_quantity,
            "created_at": self.created_at,
        }

    def deserialize(self, data):
        """Update product data from a dictionary."""
        self.sku = data["sku"]
        self.product_name = data["product_name"]
        self.description = data.get("description")
        self.price = data["price"]
        self.stock_quantity = data.get("stock_quantity", 0)

    @classmethod
    def find_by_sku(cls, sku):
        """Return a product by SKU or None."""
        return cls.query.filter_by(sku=sku).first()

    @staticmethod
    def json_schema():
        """JSON schema for product data."""
        return {
            "type": "object",
            "properties": {
                "sku": {"type": "string", "minLength": 1},
                "product_name": {"type": "string", "minLength": 1},
                "description": {"type": ["string", "null"]},
                "price": {"type": "number", "minimum": 0},
                "stock_quantity": {"type": "integer", "minimum": 0},
            },
            "required": ["sku", "product_name", "price"],
            "additionalProperties": False,
        }


class Order(ModelAccessMixin, db.Model):
    """Order model."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Text, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))

    user = db.relationship("User", back_populates="orders")
    product = db.relationship("Product", back_populates="orders")

    __table_args__ = (
        db.CheckConstraint("quantity > 0", name="quantity_positive"),
        db.CheckConstraint("status IN ('placed','paid','cancelled')", name="status_allowed"),
    )

    def serialize(self):
        """Return order data as a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "status": self.status,
            "created_at": self.created_at,
        }

    def deserialize(self, data):
        """Update order data from a dictionary."""
        self.user_id = data["user_id"]
        self.product_id = data["product_id"]
        self.quantity = data["quantity"]
        self.status = data.get("status", "placed")

    @staticmethod
    def json_schema(require_status=False):
        """JSON schema for order data."""
        required = ["user_id", "product_id", "quantity"]
        if require_status:
            required.append("status")

        return {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer"},
                "product_id": {"type": "integer"},
                "quantity": {"type": "integer", "minimum": 1},
                "status": {"type": "string", "enum": ["placed", "paid", "cancelled"]},
            },
            "required": required,
            "additionalProperties": False,
        }


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Create database tables."""
    db.create_all()
    click.echo("Database initialized.")


def populate_db():
    """Populate the database with a small coherent sample dataset."""
    user = User(email="customer@example.com", name="Example Customer")
    product = Product(
        sku="SKU-001",
        product_name="Example Product",
        description="Seed product",
        price=19.99,
        stock_quantity=10,
    )

    db.session.add(user)
    db.session.add(product)
    db.session.flush()

    order = Order(
        user_id=user.id,
        product_id=product.id,
        quantity=2,
        status="placed",
    )
    product.stock_quantity -= order.quantity

    db.session.add(order)
    db.session.commit()


@click.command("seed-db")
@with_appcontext
def seed_db_command():
    """Create tables and insert a small example dataset."""
    db.create_all()

    if User.query.first() is not None:
        click.echo("Database already contains data.")
        return

    populate_db()
    click.echo("Seed data inserted.")
