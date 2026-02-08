from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP'))

    orders = db.relationship("Order", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None,
        }


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sku = db.Column(db.String(120), nullable=False, unique=True)
    product_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP'))

    orders = db.relationship("Order", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        db.CheckConstraint('price >= 0', name='price_non_negative'),
        db.CheckConstraint('stock_quantity >= 0', name='stock_non_negative'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "product_name": self.product_name,
            "description": self.description,
            "price": self.price,
            "stock_quantity": self.stock_quantity,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None,
        }


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP'))

    user = db.relationship("User", back_populates="orders")
    product = db.relationship("Product", back_populates="orders")

    __table_args__ = (
        db.CheckConstraint('quantity > 0', name='quantity_positive'),
        db.CheckConstraint("status IN ('placed','paid','cancelled')", name='status_allowed'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None,
        }
