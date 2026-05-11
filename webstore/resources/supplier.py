"""Supplier resources."""

from flask import request, url_for
from flask_restful import Resource
from jsonschema import ValidationError, validate

from webstore import db
from webstore.constants import SUPPLIER_PROFILE
from webstore.models import Supplier
from webstore.utils import StoreBuilder, create_error_response, mason_response


class SupplierCollection(Resource):
    """Resource for the supplier collection."""

    def get(self):
        body = StoreBuilder()
        body.add_common_namespace()
        body.add_control("self", href=url_for("api.suppliercollection"))
        body.add_control_all_users()
        body.add_control_all_products()
        body.add_control_all_orders()
        body.add_control_all_categories()
        body.add_control_all_suppliers()
        body.add_control_add_supplier(Supplier.json_schema())
        body["suppliers"] = []

        for supplier in Supplier.get_all():
            item = StoreBuilder(supplier.serialize())
            item.add_control("self", href=url_for("api.supplieritem", supplier_id=supplier.id))
            item.add_control("profile", href=SUPPLIER_PROFILE)
            body["suppliers"].append(item)

        return mason_response(body)

    def post(self):
        if not request.is_json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, Supplier.json_schema())
        except ValidationError as error:
            return create_error_response(400, "Invalid JSON document", str(error))

        if Supplier.find_by_name(request.json["name"]) is not None:
            return create_error_response(409, "Conflict", "Supplier name already exists.")

        supplier = Supplier()
        supplier.deserialize(request.json)
        db.session.add(supplier)
        db.session.commit()
        return mason_response(
            {},
            status=201,
            headers={"Location": url_for("api.supplieritem", supplier_id=supplier.id)},
        )


class SupplierItem(Resource):
    """Resource for a single supplier."""

    def get(self, supplier_id):
        supplier = db.get_or_404(Supplier, supplier_id)
        body = StoreBuilder(supplier.serialize())
        body.add_common_namespace()
        body.add_control("self", href=url_for("api.supplieritem", supplier_id=supplier.id))
        body.add_control("profile", href=SUPPLIER_PROFILE)
        body.add_control("collection", href=url_for("api.suppliercollection"))
        body.add_control_edit_supplier(supplier, Supplier.json_schema())
        body.add_control_delete_supplier(supplier)
        return mason_response(body)

    def put(self, supplier_id):
        supplier = db.get_or_404(Supplier, supplier_id)
        if not request.is_json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, Supplier.json_schema())
        except ValidationError as error:
            return create_error_response(400, "Invalid JSON document", str(error))

        existing = Supplier.find_by_name(request.json["name"])
        if existing is not None and existing.id != supplier.id:
            return create_error_response(409, "Conflict", "Supplier name already exists.")

        supplier.deserialize(request.json)
        db.session.add(supplier)
        db.session.commit()
        return "", 204

    def delete(self, supplier_id):
        supplier = db.get_or_404(Supplier, supplier_id)
        db.session.delete(supplier)
        db.session.commit()
        return "", 204
