"""Application factory for the webstore API."""

from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

from webstore.constants import LINK_RELATIONS_URL


db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """Enable foreign key enforcement for SQLite connections."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    default_config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///webstore.db",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }

    app.config.from_mapping(default_config)
    if test_config is not None:
        app.config.from_mapping(test_config)

    db.init_app(app)

    from webstore import api, models
    from webstore import swagger

    app.cli.add_command(models.init_db_command)
    app.cli.add_command(models.seed_db_command)
    app.register_blueprint(api.api_bp)
    app.register_blueprint(swagger.bp)

    @app.route("/")
    def index():
        return redirect(url_for("client"))

    @app.route("/api-info/")
    def api_info():
        return {
            "name": "Webstore API",
            "api": "/api/",
            "client": "/client/",
            "resources": {
                "users": "/api/users/",
                "products": "/api/products/",
                "orders": "/api/orders/",
                "categories": "/api/categories/",
                "suppliers": "/api/suppliers/",
            },
        }

    @app.route("/client/")
    def client():
        return redirect(url_for("static", filename="client/index.html"))

    @app.route(LINK_RELATIONS_URL)
    def send_link_relations():
        return {
            "self": LINK_RELATIONS_URL,
            "relations": [
                "user:add-user",
                "product:add-product",
                "order:add-order",
                "category:add-category",
                "supplier:add-supplier",
            ],
        }

    @app.route("/profiles/<profile>/")
    def send_profile(profile):
        return {"profile": profile}

    return app


def main():
    """Run the development server."""
    app = create_app()
    app.run(debug=True)


if __name__ == "__main__":
    main()
