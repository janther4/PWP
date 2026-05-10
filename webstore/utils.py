"""Utility helpers for the webstore API."""

import json

from flask import Response, request, url_for

from webstore.constants import (
    ERROR_PROFILE,
    LINK_RELATIONS_URL,
    MASON,
    ORDER_PROFILE,
    PRODUCT_PROFILE,
    USER_PROFILE,
)


class MasonBuilder(dict):
    """Convenience class for building Mason-like JSON documents."""

    def add_namespace(self, ns, uri):
        """Add a namespace definition."""
        if "@namespaces" not in self:
            self["@namespaces"] = {}
        self["@namespaces"][ns] = {"name": uri}

    def add_control(self, ctrl_name, href, **kwargs):
        """Add a hypermedia control."""
        if "@controls" not in self:
            self["@controls"] = {}
        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href

    def add_error(self, title, details):
        """Add an error object."""
        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_control_post(self, ctrl_name, title, href, schema):
        """Add a POST control."""
        self.add_control(
            ctrl_name,
            href,
            method="POST",
            encoding="json",
            title=title,
            schema=schema,
        )

    def add_control_put(self, title, href, schema):
        """Add a PUT edit control."""
        self.add_control(
            "edit",
            href,
            method="PUT",
            encoding="json",
            title=title,
            schema=schema,
        )

    def add_control_delete(self, title, href):
        """Add a DELETE control."""
        self.add_control("delete", href, method="DELETE", title=title)


class StoreBuilder(MasonBuilder):
    """Application-specific Mason helpers."""

    def add_common_namespace(self):
        """Add the webstore namespace."""
        self.add_namespace("store", LINK_RELATIONS_URL)

    def add_control_all_users(self):
        """Add a control for the user collection."""
        self.add_control(
            "store:get-users",
            url_for("api.usercollection"),
            method="GET",
            title="Get all users",
        )

    def add_control_all_products(self):
        """Add a control for the product collection."""
        self.add_control(
            "store:get-products",
            url_for("api.productcollection"),
            method="GET",
            title="Get all products",
        )

    def add_control_all_orders(self):
        """Add a control for the order collection."""
        self.add_control(
            "store:get-orders",
            url_for("api.ordercollection"),
            method="GET",
            title="Get all orders",
        )

    def add_control_add_user(self, schema):
        """Add a control for creating a user."""
        self.add_control_post(
            "user:add-user",
            "Add a new user",
            url_for("api.usercollection"),
            schema,
        )

    def add_control_add_product(self, schema):
        """Add a control for creating a product."""
        self.add_control_post(
            "product:add-product",
            "Add a new product",
            url_for("api.productcollection"),
            schema,
        )

    def add_control_add_order(self, schema):
        """Add a control for creating an order."""
        self.add_control_post(
            "order:add-order",
            "Add a new order",
            url_for("api.ordercollection"),
            schema,
        )

    def add_control_edit_user(self, user, schema):
        """Add a control for editing a user."""
        self.add_control_put("Edit a user", url_for("api.useritem", user_id=user.id), schema)

    def add_control_edit_product(self, product, schema):
        """Add a control for editing a product."""
        self.add_control_put(
            "Edit a product",
            url_for("api.productitem", product_id=product.id),
            schema,
        )

    def add_control_edit_order(self, order, schema):
        """Add a control for editing an order."""
        self.add_control_put("Edit an order", url_for("api.orderitem", order_id=order.id), schema)

    def add_control_delete_user(self, user):
        """Add a control for deleting a user."""
        self.add_control_delete("Delete a user", url_for("api.useritem", user_id=user.id))

    def add_control_delete_product(self, product):
        """Add a control for deleting a product."""
        self.add_control_delete(
            "Delete a product",
            url_for("api.productitem", product_id=product.id),
        )

    def add_control_delete_order(self, order):
        """Add a control for deleting an order."""
        self.add_control_delete("Delete an order", url_for("api.orderitem", order_id=order.id))

    def add_control_user(self, user_id):
        """Add a control to a user item."""
        self.add_control(
            "order:get-user",
            url_for("api.useritem", user_id=user_id),
            method="GET",
            title="Get the user for this order",
        )

    def add_control_product(self, product_id):
        """Add a control to a product item."""
        self.add_control(
            "order:get-product",
            url_for("api.productitem", product_id=product_id),
            method="GET",
            title="Get the product for this order",
        )


def mason_response(body, status=200, headers=None):
    """Return a Mason-like JSON response."""
    return Response(json.dumps(body), status=status, headers=headers, mimetype=MASON)


def create_error_response(status_code, title, message=None):
    """Create a consistent error response."""
    body = MasonBuilder(resource_url=request.path)
    body.add_error(title, message or title)
    body.add_control("profile", href=ERROR_PROFILE)
    return mason_response(body, status=status_code)


def add_resource_controls(item, profile):
    """Add common item controls."""
    item.add_control("profile", href=profile)


def profile_for_resource(resource):
    """Return the profile URL for a resource name."""
    profiles = {
        "user": USER_PROFILE,
        "product": PRODUCT_PROFILE,
        "order": ORDER_PROFILE,
    }
    return profiles[resource]