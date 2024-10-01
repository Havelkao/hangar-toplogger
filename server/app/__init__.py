from .config import config
from flask import Flask
from .extensions import htmx


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_blueprints(app)
    register_extensions(app)

    return app


def register_extensions(app):
    """Register Flask extensions."""
    htmx.init_app(app)


def register_blueprints(app):
    """Register Flask blueprints."""
    from .routes import main as main_bp
    from .routes import auth as auth_bp

    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/auth")
