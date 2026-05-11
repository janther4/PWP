"""Application factory for the webstore API."""

from flask import Flask
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

    app.cli.add_command(models.init_db_command)
    app.cli.add_command(models.seed_db_command)
    app.register_blueprint(api.api_bp)

    @app.route("/")
    def index():
        return {
            "name": "Webstore API",
            "api": "/api/",
            "resources": {
                "users": "/api/users/",
                "products": "/api/products/",
                "orders": "/api/orders/",
                "categories": "/api/categories/",
                "suppliers": "/api/suppliers/",
            },
        }

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
