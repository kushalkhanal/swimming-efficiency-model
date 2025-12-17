"""
Route registration helpers for the REST API blueprints.
"""

from flask import Flask

from .processing import processing_bp
from .uploads import upload_bp
from .metrics import metrics_bp
from .frames import frames_bp
from .reports import reports_bp


def register_blueprints(app: Flask) -> None:
    """
    Attach versioned blueprints to the Flask app.

    Namespaces follow `/api/v1/...` to simplify future versioning.
    """
    app.register_blueprint(upload_bp, url_prefix="/api/v1")
    app.register_blueprint(processing_bp, url_prefix="/api/v1")
    app.register_blueprint(metrics_bp, url_prefix="/api/v1")
    app.register_blueprint(frames_bp, url_prefix="/api/v1")
    app.register_blueprint(reports_bp, url_prefix="/api/v1")

