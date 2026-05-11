"""User resources."""

from flask import request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate

from webstore import db
from webstore.constants import USER_PROFILE
from webstore.models import User
from webstore.utils import StoreBuilder, create_error_response, mason_response


class UserCollection(Resource):
    """Resource for the user collection."""

    def get(self):
        body = StoreBuilder()
        body.add_common_namespace()
        body.add_control("self", href=url_for("api.usercollection"))
        body.add_control_all_users()
        body.add_control_all_products()
        body.add_control_all_orders()
        body.add_control_all_categories()
        body.add_control_all_suppliers()
        body.add_control_add_user(User.json_schema())
        body["users"] = []

        for user in User.get_all():
            item = StoreBuilder(user.serialize())
            item.add_control("self", href=url_for("api.useritem", user_id=user.id))
            item.add_control("profile", href=USER_PROFILE)
            body["users"].append(item)

        return mason_response(body)

    def post(self):
        if not request.is_json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, User.json_schema())
        except ValidationError as error:
            return create_error_response(400, "Invalid JSON document", str(error))

        if User.find_by_email(request.json["email"]) is not None:
            return create_error_response(409, "Conflict", "Email already exists.")

        user = User()
        user.deserialize(request.json)
        db.session.add(user)
        db.session.commit()
        return mason_response(
            {},
            status=201,
            headers={"Location": url_for("api.useritem", user_id=user.id)},
        )


class UserItem(Resource):
    """Resource for a single user."""

    def get(self, user_id):
        user = db.get_or_404(User, user_id)
        body = StoreBuilder(user.serialize())
        body.add_common_namespace()
        body.add_control("self", href=url_for("api.useritem", user_id=user.id))
        body.add_control("profile", href=USER_PROFILE)
        body.add_control("collection", href=url_for("api.usercollection"))
        body.add_control_edit_user(user, User.json_schema())
        body.add_control_delete_user(user)
        body.add_control_all_orders()
        return mason_response(body)

    def put(self, user_id):
        user = db.get_or_404(User, user_id)
        if not request.is_json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, User.json_schema())
        except ValidationError as error:
            return create_error_response(400, "Invalid JSON document", str(error))

        existing = User.find_by_email(request.json["email"])
        if existing is not None and existing.id != user.id:
            return create_error_response(409, "Conflict", "Email already exists.")

        user.deserialize(request.json)
        db.session.add(user)
        db.session.commit()
        return "", 204

    def delete(self, user_id):
        user = db.get_or_404(User, user_id)
        db.session.delete(user)
        db.session.commit()
        return "", 204
