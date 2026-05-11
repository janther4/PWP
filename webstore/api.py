"""API blueprint and resource routing."""

from flask import Blueprint
from flask_restful import Api

from webstore.resources.category import CategoryCollection, CategoryItem
from webstore.resources.order import OrderCollection, OrderItem
from webstore.resources.product import ProductCollection, ProductItem
from webstore.resources.supplier import SupplierCollection, SupplierItem
from webstore.resources.user import UserCollection, UserItem


api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(UserCollection, "/users/", endpoint="usercollection")
api.add_resource(UserItem, "/users/<int:user_id>/", endpoint="useritem")

api.add_resource(ProductCollection, "/products/", endpoint="productcollection")
api.add_resource(ProductItem, "/products/<int:product_id>/", endpoint="productitem")

api.add_resource(OrderCollection, "/orders/", endpoint="ordercollection")
api.add_resource(OrderItem, "/orders/<int:order_id>/", endpoint="orderitem")

api.add_resource(CategoryCollection, "/categories/", endpoint="categorycollection")
api.add_resource(CategoryItem, "/categories/<int:category_id>/", endpoint="categoryitem")

api.add_resource(SupplierCollection, "/suppliers/", endpoint="suppliercollection")
api.add_resource(SupplierItem, "/suppliers/<int:supplier_id>/", endpoint="supplieritem")
