import os

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from .database import init_app as init_database
from .database import init_db
from .errors import AppError
from .routes.item_routes import bp as item_bp
from .routes.loan_routes import bp as loan_bp


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    default_database = os.path.join(app.instance_path, "lab_equipment.db")
    app.config.from_mapping(
        DATABASE=os.environ.get("LAB_DATABASE", default_database),
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    init_database(app)
    app.register_blueprint(item_bp)
    app.register_blueprint(loan_bp)
    _register_error_handlers(app)

    with app.app_context():
        init_db()

    return app


def _register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Internal server error"}), 500
