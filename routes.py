from flask import Blueprint, request, jsonify
from models import db, Product, User, Order

api = Blueprint("api", __name__)


@api.route("/products", methods=["POST"])
def create_product():
    data = request.get_json() or {}
    required = ["sku", "product_name", "price"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    product = Product(
        sku=data["sku"],
        product_name=data["product_name"],
        description=data.get("description"),
        price=data["price"],
        stock_quantity=data.get("stock_quantity", 0),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@api.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])


@api.route("/users", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    if "email" not in data or "name" not in data:
        return jsonify({"error": "Missing 'email' or 'name'"}), 400

    user = User(email=data["email"], name=data["name"])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@api.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])


@api.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json() or {}
    required = ["user_id", "product_id", "quantity"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    user = User.query.get(data["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    product = Product.query.get(data["product_id"])
    if not product:
        return jsonify({"error": "Product not found"}), 404

    qty = int(data["quantity"])
    if qty <= 0:
        return jsonify({"error": "Quantity must be > 0"}), 400

    if product.stock_quantity < qty:
        return jsonify({"error": "Not enough stock"}), 400

    status = data.get("status", "placed")
    if status not in ("placed", "paid", "cancelled"):
        return jsonify({"error": "Invalid status"}), 400

    order = Order(user_id=user.id, product_id=product.id, quantity=qty, status=status)
    # deduct stock
    product.stock_quantity = product.stock_quantity - qty

    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201


@api.route("/orders", methods=["GET"])
def get_orders():
    orders = Order.query.all()
    return jsonify([o.to_dict() for o in orders])
