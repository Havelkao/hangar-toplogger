from flask import Flask
from .extensions import htmx


def create_app():
    app = Flask(__name__)

    register_blueprints(app)
    register_extensions(app)

    return app


def register_extensions(app):
    """Register Flask extensions."""
    htmx.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    from .routes import main as main_bp

    app.register_blueprint(main_bp, url_prefix="/")
