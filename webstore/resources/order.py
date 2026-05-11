"""Order resources."""

from flask import request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate

from webstore import db
from webstore.constants import ORDER_PROFILE
from webstore.models import Order, Product, User
from webstore.utils import StoreBuilder, create_error_response, mason_response


class OrderCollection(Resource):
    """Resource for the order collection."""

    def get(self):
        """Return all orders."""
        body = StoreBuilder()
        body.add_common_namespace()
        body.add_control("self", href=url_for("api.ordercollection"))
        body.add_control_all_users()
        body.add_control_all_products()
        body.add_control_all_orders()
        body.add_control_all_categories()
        body.add_control_all_suppliers()
        body.add_control_add_order(Order.json_schema())
        body["orders"] = []

        for order in Order.get_all():
            item = StoreBuilder(order.serialize())
            item.add_control("self", href=url_for("api.orderitem", order_id=order.id))
            item.add_control("profile", href=ORDER_PROFILE)
            body["orders"].append(item)

        return mason_response(body)

    def post(self):
        """Create an order and deduct stock."""
        if not request.is_json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, Order.json_schema())
        except ValidationError as error:
            return create_error_response(400, "Invalid JSON document", str(error))

        user = User.get_by_id(request.json["user_id"])
        if user is None:
            return create_error_response(404, "Not found", "User not found.")

        product = Product.get_by_id(request.json["product_id"])
        if product is None:
            return create_error_response(404, "Not found", "Product not found.")

        quantity = request.json["quantity"]
        if product.stock_quantity < quantity:
            return create_error_response(409, "Conflict", "Not enough stock.")

        order = Order()
        order.deserialize(request.json)
        product.stock_quantity -= quantity

        db.session.add(order)
        db.session.commit()

        return mason_response(
            {},
            status=201,
            headers={"Location": url_for("api.orderitem", order_id=order.id)},
        )


class OrderItem(Resource):
    """Resource for a single order."""

    def get(self, order_id):
        """Return an order."""
        order = db.get_or_404(Order, order_id)
        body = StoreBuilder(order.serialize())
        body.add_common_namespace()
        body.add_control("self", href=url_for("api.orderitem", order_id=order.id))
        body.add_control("profile", href=ORDER_PROFILE)
        body.add_control("collection", href=url_for("api.ordercollection"))
        body.add_control_user(order.user_id)
        body.add_control_product(order.product_id)
        body.add_control_edit_order(order, Order.json_schema(require_status=True))
        body.add_control_delete_order(order)
        return mason_response(body)

    def put(self, order_id):
        """Replace an order and keep stock quantities consistent."""
        order = db.get_or_404(Order, order_id)
        if not request.is_json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, Order.json_schema(require_status=True))
        except ValidationError as error:
            return create_error_response(400, "Invalid JSON document", str(error))

        user = User.get_by_id(request.json["user_id"])
        if user is None:
            return create_error_response(404, "Not found", "User not found.")

        old_product = Product.get_by_id(order.product_id)
        new_product = Product.get_by_id(request.json["product_id"])
        if new_product is None:
            return create_error_response(404, "Not found", "Product not found.")

        if old_product is not None:
            old_product.stock_quantity += order.quantity

        if new_product.stock_quantity < request.json["quantity"]:
            db.session.rollback()
            return create_error_response(409, "Conflict", "Not enough stock.")

        new_product.stock_quantity -= request.json["quantity"]
        order.deserialize(request.json)

        db.session.add(order)
        db.session.commit()
        return "", 204

    def delete(self, order_id):
        """Delete an order and restore stock."""
        order = db.get_or_404(Order, order_id)
        product = Product.get_by_id(order.product_id)
        if product is not None:
            product.stock_quantity += order.quantity

        db.session.delete(order)
        db.session.commit()
        return "", 204
