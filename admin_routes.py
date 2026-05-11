from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from models import Order, Product, User, db

admin = Blueprint("admin", __name__, url_prefix="/admin")

ALLOWED_ORDER_STATUSES = ("placed", "paid", "cancelled")


@admin.route("/")
def dashboard():
    return render_template(
        "admin/dashboard.html",
        product_count=Product.query.count(),
        user_count=User.query.count(),
        order_count=Order.query.count(),
    )


@admin.route("/products")
def products():
    products_list = Product.query.order_by(Product.id.desc()).all()
    return render_template("admin/products.html", products=products_list)


@admin.route("/products/new", methods=["GET", "POST"])
def create_product():
    if request.method == "POST":
        sku = (request.form.get("sku") or "").strip()
        product_name = (request.form.get("product_name") or "").strip()
        description = (request.form.get("description") or "").strip() or None

        try:
            price = float(request.form.get("price", "").strip())
            stock_quantity = int(request.form.get("stock_quantity", "0").strip())
        except ValueError:
            flash("Price must be a number and stock must be an integer.", "error")
            return render_template("admin/product_form.html", product=None)

        if not sku or not product_name:
            flash("SKU and product name are required.", "error")
            return render_template("admin/product_form.html", product=None)
        if price < 0 or stock_quantity < 0:
            flash("Price and stock must be non-negative.", "error")
            return render_template("admin/product_form.html", product=None)

        product = Product(
            sku=sku,
            product_name=product_name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
        )
        db.session.add(product)
        try:
            db.session.commit()
            flash("Product created.", "success")
            return redirect(url_for("admin.products"))
        except IntegrityError:
            db.session.rollback()
            flash("SKU must be unique.", "error")

    return render_template("admin/product_form.html", product=None)


@admin.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("admin.products"))

    if request.method == "POST":
        sku = (request.form.get("sku") or "").strip()
        product_name = (request.form.get("product_name") or "").strip()
        description = (request.form.get("description") or "").strip() or None

        try:
            price = float(request.form.get("price", "").strip())
            stock_quantity = int(request.form.get("stock_quantity", "0").strip())
        except ValueError:
            flash("Price must be a number and stock must be an integer.", "error")
            return render_template("admin/product_form.html", product=product)

        if not sku or not product_name:
            flash("SKU and product name are required.", "error")
            return render_template("admin/product_form.html", product=product)
        if price < 0 or stock_quantity < 0:
            flash("Price and stock must be non-negative.", "error")
            return render_template("admin/product_form.html", product=product)

        product.sku = sku
        product.product_name = product_name
        product.description = description
        product.price = price
        product.stock_quantity = stock_quantity

        try:
            db.session.commit()
            flash("Product updated.", "success")
            return redirect(url_for("admin.products"))
        except IntegrityError:
            db.session.rollback()
            flash("SKU must be unique.", "error")

    return render_template("admin/product_form.html", product=product)


@admin.route("/products/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("admin.products"))

    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "success")
    return redirect(url_for("admin.products"))


@admin.route("/users")
def users():
    users_list = User.query.order_by(User.id.desc()).all()
    return render_template("admin/users.html", users=users_list)


@admin.route("/users/new", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        name = (request.form.get("name") or "").strip()

        if not email or not name:
            flash("Email and name are required.", "error")
            return render_template("admin/user_form.html")

        user = User(email=email, name=name)
        db.session.add(user)
        try:
            db.session.commit()
            flash("User created.", "success")
            return redirect(url_for("admin.users"))
        except IntegrityError:
            db.session.rollback()
            flash("Email must be unique.", "error")

    return render_template("admin/user_form.html")


@admin.route("/orders")
def orders():
    orders_list = (
        Order.query.join(User, Order.user_id == User.id)
        .join(Product, Order.product_id == Product.id)
        .order_by(Order.id.desc())
        .all()
    )
    return render_template(
        "admin/orders.html",
        orders=orders_list,
        allowed_statuses=ALLOWED_ORDER_STATUSES,
    )


@admin.route("/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    order = db.session.get(Order, order_id)
    if order is None:
        flash("Order not found.", "error")
        return redirect(url_for("admin.orders"))

    new_status = (request.form.get("status") or "").strip()
    if new_status not in ALLOWED_ORDER_STATUSES:
        flash("Invalid status.", "error")
        return redirect(url_for("admin.orders"))

    order.status = new_status
    db.session.commit()
    flash("Order status updated.", "success")
    return redirect(url_for("admin.orders"))
