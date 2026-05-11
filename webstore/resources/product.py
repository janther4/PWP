"""Product resources."""

from flask import request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate

from webstore import db
from webstore.constants import PRODUCT_PROFILE
from webstore.models import Product
from webstore.utils import StoreBuilder, create_error_response, mason_response


class ProductCollection(Resource):
    """Resource for the product collection."""

    def get(self):
        body = StoreBuilder()
        body.add_common_namespace()
        body.add_control("self", href=url_for("api.productcollection"))
        body.add_control_all_users()
        body.add_control_all_products()
        body.add_control_all_orders()
        body.add_control_all_categories()
        body.add_control_all_suppliers()
        body.add_control_add_product(Product.json_schema())
        body["products"] = []

        for product in Product.get_all():
            item = StoreBuilder(product.serialize())
            item.add_control("self", href=url_for("api.productitem", product_id=product.id))
            item.add_control("profile", href=PRODUCT_PROFILE)
            body["products"].append(item)

        return mason_response(body)

    def post(self):
        if not request.is_json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, Product.json_schema())
        except ValidationError as error:
            return create_error_response(400, "Invalid JSON document", str(error))

        if Product.find_by_sku(request.json["sku"]) is not None:
            return create_error_response(409, "Conflict", "SKU already exists.")

        product = Product()
        product.deserialize(request.json)
        db.session.add(product)
        db.session.commit()
        return mason_response(
            {},
            status=201,
            headers={"Location": url_for("api.productitem", product_id=product.id)},
        )


class ProductItem(Resource):
    """Resource for a single product."""

    def get(self, product_id):
        product = db.get_or_404(Product, product_id)
        body = StoreBuilder(product.serialize())
        body.add_common_namespace()
        body.add_control("self", href=url_for("api.productitem", product_id=product.id))
        body.add_control("profile", href=PRODUCT_PROFILE)
        body.add_control("collection", href=url_for("api.productcollection"))
        body.add_control_edit_product(product, Product.json_schema())
        body.add_control_delete_product(product)
        body.add_control_all_orders()
        return mason_response(body)

    def put(self, product_id):
        product = db.get_or_404(Product, product_id)
        if not request.is_json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, Product.json_schema())
        except ValidationError as error:
            return create_error_response(400, "Invalid JSON document", str(error))

        existing = Product.find_by_sku(request.json["sku"])
        if existing is not None and existing.id != product.id:
            return create_error_response(409, "Conflict", "SKU already exists.")

        product.deserialize(request.json)
        db.session.add(product)
        db.session.commit()
        return "", 204

    def delete(self, product_id):
        product = db.get_or_404(Product, product_id)
        db.session.delete(product)
        db.session.commit()
        return "", 204
