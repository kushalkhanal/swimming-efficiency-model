"""
Application factory for the biomechanical swimming analytics backend.

This module wires together configuration, database connections, background
workers, and REST API blueprints. Business logic lives in the `services`
package while HTTP routes are defined under `routes`.
"""

from pathlib import Path

from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_socketio import SocketIO

from .config import get_config
from .db.client import init_mongo
from .routes import register_blueprints
from .utils.logging_config import setup_logging, get_logger

# Global SocketIO instance for emitting events from services
socketio = SocketIO()
logger = get_logger(__name__)


def create_app(config_name: str | None = None) -> Flask:
    """
    Build and configure the Flask application instance.

    Args:
        config_name: Optional configuration profile. Falls back to
            `OFFLINE_DEV` when not provided.
    """
    config = get_config(config_name)
    
    # Setup logging before anything else
    setup_logging(
        app_name="swim-analytics",
        log_level="DEBUG" if config.DEBUG else "INFO",
        log_dir=Path("./logs") if not config.DEBUG else None,
        json_format=not config.DEBUG,
    )
    logger.info("Starting application", extra_data={"config": config_name or "OFFLINE_DEV"})

    app = Flask(__name__)
    app.config.from_object(config)

    # Set maximum upload size (500MB for video files)
    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

    # Enable CORS for the offline frontend served from localhost.
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    # Initialize MongoDB client and attach to Flask app context.
    app.mongo = init_mongo(app.config)  # type: ignore[attr-defined]

    # Register versioned API blueprints.
    register_blueprints(app)

    # Initialize SocketIO with the app
    socketio.init_app(
        app,
        cors_allowed_origins=app.config["CORS_ORIGINS"],
        async_mode="threading"
    )

    # Request logging middleware
    @app.before_request
    def log_request_start():
        import uuid
        import time
        g.request_id = uuid.uuid4().hex[:8]
        g.start_time = time.time()
        logger.info(
            f"{request.method} {request.path}",
            request_id=g.request_id,
            extra_data={"args": dict(request.args)}
        )

    @app.after_request
    def log_request_end(response):
        import time
        duration = (time.time() - g.get("start_time", 0)) * 1000
        logger.info(
            f"{request.method} {request.path} → {response.status_code}",
            request_id=g.get("request_id"),
            extra_data={"duration_ms": round(duration, 2), "status": response.status_code}
        )
        return response

    @app.get("/healthz")
    def healthcheck() -> dict[str, str]:
        """Simple health endpoint used by local monitoring scripts."""
        return {"status": "ok"}

    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle file size limit exceeded errors."""
        return jsonify({"error": "File size exceeds the maximum limit of 500MB"}), 413

    return app


def get_socketio() -> SocketIO:
    """Get the global SocketIO instance."""
    return socketio

