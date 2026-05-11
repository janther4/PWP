from flask import Flask, redirect, url_for
from config import Config
from models import db
from routes import api
from admin_routes import admin

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"

    db.init_app(app)
    app.register_blueprint(api)
    app.register_blueprint(admin)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return redirect(url_for("admin.dashboard"))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
