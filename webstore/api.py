"""API blueprint and resource registration."""

from flask import Blueprint
from flask_restful import Api

from webstore.resources.order import OrderCollection, OrderItem
from webstore.resources.product import ProductCollection, ProductItem
from webstore.resources.user import UserCollection, UserItem
from webstore.resources.category import CategoryCollection, CategoryItem
from webstore.resources.supplier import SupplierCollection, SupplierItem


api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

bp = api_bp

api.add_resource(UserCollection, "/users/", methods=["GET", "POST"])
api.add_resource(UserItem, "/users/<int:user_id>/", methods=["GET", "PUT", "DELETE"])

api.add_resource(ProductCollection, "/products/", methods=["GET", "POST"])
api.add_resource(ProductItem, "/products/<int:product_id>/", methods=["GET", "PUT", "DELETE"])

api.add_resource(CategoryCollection, "/categories/", methods=["GET", "POST"])
api.add_resource(CategoryItem, "/categories/<int:category_id>/", methods=["GET", "PUT", "DELETE"])

api.add_resource(SupplierCollection, "/suppliers/", methods=["GET", "POST"])
api.add_resource(SupplierItem, "/suppliers/<int:supplier_id>/", methods=["GET", "PUT", "DELETE"])

api.add_resource(OrderCollection, "/orders/", methods=["GET", "POST"])
api.add_resource(OrderItem, "/orders/<int:order_id>/", methods=["GET", "PUT", "DELETE"])