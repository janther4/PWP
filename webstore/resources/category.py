"""Category resources."""

from flask import request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate

from webstore import db
from webstore.constants import CATEGORY_PROFILE
from webstore.models import Category
from webstore.utils import StoreBuilder, create_error_response, mason_response


class CategoryCollection(Resource):
    """Resource for the category collection."""

    def get(self):
        body = StoreBuilder()
        body.add_common_namespace()
        body.add_control("self", href=url_for("api.categorycollection"))
        body.add_control_all_users()
        body.add_control_all_products()
        body.add_control_all_orders()
        body.add_control_all_categories()
        body.add_control_all_suppliers()
        body.add_control_add_category(Category.json_schema())
        body["categories"] = []

        for category in Category.get_all():
            item = StoreBuilder(category.serialize())
            item.add_control("self", href=url_for("api.categoryitem", category_id=category.id))
            item.add_control("profile", href=CATEGORY_PROFILE)
            body["categories"].append(item)

        return mason_response(body)

    def post(self):
        if not request.is_json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, Category.json_schema())
        except ValidationError as error:
            return create_error_response(400, "Invalid JSON document", str(error))

        if Category.find_by_name(request.json["name"]) is not None:
            return create_error_response(409, "Conflict", "Category name already exists.")

        category = Category()
        category.deserialize(request.json)
        db.session.add(category)
        db.session.commit()
        return mason_response(
            {},
            status=201,
            headers={"Location": url_for("api.categoryitem", category_id=category.id)},
        )


class CategoryItem(Resource):
    """Resource for a single category."""

    def get(self, category_id):
        category = db.get_or_404(Category, category_id)
        body = StoreBuilder(category.serialize())
        body.add_common_namespace()
        body.add_control("self", href=url_for("api.categoryitem", category_id=category.id))
        body.add_control("profile", href=CATEGORY_PROFILE)
        body.add_control("collection", href=url_for("api.categorycollection"))
        body.add_control_edit_category(category, Category.json_schema())
        body.add_control_delete_category(category)
        return mason_response(body)

    def put(self, category_id):
        category = db.get_or_404(Category, category_id)
        if not request.is_json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, Category.json_schema())
        except ValidationError as error:
            return create_error_response(400, "Invalid JSON document", str(error))

        existing = Category.find_by_name(request.json["name"])
        if existing is not None and existing.id != category.id:
            return create_error_response(409, "Conflict", "Category name already exists.")

        category.deserialize(request.json)
        db.session.add(category)
        db.session.commit()
        return "", 204

    def delete(self, category_id):
        category = db.get_or_404(Category, category_id)
        db.session.delete(category)
        db.session.commit()
        return "", 204
