"""Database models for the webstore API.

    GitHub Copilot used for iterative development and docstrings.
"""

import click
from flask.cli import with_appcontext

from webstore import db


class ModelAccessMixin:
    """Small access helper mixin for model queries and persistence."""

    @classmethod
    def get_all(cls):
        """Fetch all rows from the database ordered by the primary key.

        Returns a list of model instances.
        """
        return cls.query.order_by(cls.id).all()

    @classmethod
    def get_by_id(cls, row_id):
        """Retrieve a single row by its primary key.

        Args:
            row_id: The primary key (id) of the row.

        Returns the model instance or None if not found.
        """
        return db.session.get(cls, row_id)

    def save(self):
        """Persist the current model instance to the database.

        Adds the instance to the session and commits the transaction.

        Returns:
            self: The saved instance.
        """
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete the current model instance from the database and commit the change."""
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
        """Return a dict representation of the user for JSON serialization."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at,
        }

    def deserialize(self, data):
        """Populate the user instance from a dictionary.

        Args:
            data: A dict containing at least the keys 'email' and 'name'.
        """
        self.email = data["email"]
        self.name = data["name"]

    @classmethod
    def find_by_email(cls, email):
        """Find a user by email and return the first match or None."""
        return cls.query.filter_by(email=email).first()

    @staticmethod
    def json_schema():
        """Return a JSON Schema describing the user for input validation.

        Used by the API to validate request payloads.
        """
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
        """Return a dict representation of the product for JSON serialization."""
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
        """Populate the product fields from a dictionary.

        Args:
            data: A dict describing the product. Required keys: 'sku', 'product_name', 'price'.
        """
        self.sku = data["sku"]
        self.product_name = data["product_name"]
        self.description = data.get("description")
        self.price = data["price"]
        self.stock_quantity = data.get("stock_quantity", 0)

    @classmethod
    def find_by_sku(cls, sku):
        """Find a product by SKU and return the first match or None."""
        return cls.query.filter_by(sku=sku).first()

    @staticmethod
    def json_schema():
        """Return a JSON Schema describing the product for input validation.

        Includes types, minimums and required fields.
        """
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
        """Return a dict representation of the order for JSON serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "status": self.status,
            "created_at": self.created_at,
        }

    def deserialize(self, data):
        """Populate the order fields from a dictionary.

        Args:
            data: A dict containing at least 'user_id', 'product_id' and 'quantity'.
        """
        self.user_id = data["user_id"]
        self.product_id = data["product_id"]
        self.quantity = data["quantity"]
        self.status = data.get("status", "placed")

    @staticmethod
    def json_schema(require_status=False):
        """Return a JSON Schema describing the order for input validation.

        Args:
            require_status: If True, include 'status' in the required fields.
        """
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


class Supplier(ModelAccessMixin, db.Model):
    """Supplier model."""

    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=True)
    phone = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.Text, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))

    def serialize(self):
        """Return a dict representation of the supplier for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "created_at": self.created_at,
        }

    def deserialize(self, data):
        """Populate the supplier fields from a dictionary.

        Args:
            data: A dict that contains at least the key 'name'.
        """
        self.name = data["name"]
        self.email = data.get("email")
        self.phone = data.get("phone")

    @classmethod
    def find_by_name(cls, name):
        """Find a supplier by name and return the first match or None."""
        return cls.query.filter_by(name=name).first()

    @staticmethod
    def json_schema():
        """Return a JSON Schema describing the supplier for input validation."""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "email": {"type": ["string", "null"]},
                "phone": {"type": ["string", "null"]},
            },
            "required": ["name"],
            "additionalProperties": False,
        }


class Category(ModelAccessMixin, db.Model):
    """Category model."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.Text, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))

    def serialize(self):
        """Return a dict representation of the category for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
        }

    def deserialize(self, data):
        """Populate the category fields from a dictionary.

        Args:
            data: A dict that contains at least the key 'name'.
        """
        self.name = data["name"]
        self.description = data.get("description")

    @classmethod
    def find_by_name(cls, name):
        """Find a category by name and return the first match or None."""
        return cls.query.filter_by(name=name).first()

    @staticmethod
    def json_schema():
        """Palauttaa JSON Schema -kuvauksen kategorian validointiin."""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "description": {"type": ["string", "null"]},
            },
            "required": ["name"],
            "additionalProperties": False,
        }


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Create database tables."""
    db.create_all()
    click.echo("Database initialized.")


def populate_db():
    """Populate the database with a coherent sample dataset."""
    category = Category(name="Electronics", description="Electronic devices and accessories")
    supplier = Supplier(name="Default Supplier", email="supplier@example.com", phone="+35840111222")
    user = User(email="customer@example.com", name="Example Customer")
    product = Product(
        sku="SKU-001",
        product_name="Example Product",
        description="Seed product",
        price=19.99,
        stock_quantity=10,
    )

    db.session.add_all([category, supplier, user, product])
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
