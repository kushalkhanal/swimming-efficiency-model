"""
Structured logging configuration for the swimming analytics backend.

Provides JSON-formatted logs for production and human-readable logs for development.
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
import json


class JSONFormatter(logging.Formatter):
    """
    Formats log records as JSON for structured logging.
    Useful for log aggregation tools (ELK, CloudWatch, etc.)
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_data["data"] = record.extra_data
            
        # Add request context if available
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "video_id"):
            log_data["video_id"] = record.video_id
            
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """
    Human-readable colored output for development.
    """
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        
        # Format timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Build the message
        msg = f"{color}[{timestamp}] {record.levelname:8}{self.RESET} "
        msg += f"\033[90m{record.name}\033[0m: "
        msg += record.getMessage()
        
        # Add extra context if present
        if hasattr(record, "video_id"):
            msg += f" \033[90m[video:{record.video_id}]\033[0m"
        if hasattr(record, "request_id"):
            msg += f" \033[90m[req:{record.request_id}]\033[0m"
            
        # Add exception if present
        if record.exc_info:
            msg += "\n" + self.formatException(record.exc_info)
            
        return msg


class ContextLogger(logging.LoggerAdapter):
    """
    Logger adapter that allows adding context to log messages.
    
    Usage:
        logger = get_logger(__name__)
        logger.info("Processing video", video_id="abc123")
    """
    
    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict]:
        # Extract extra fields from kwargs
        extra = kwargs.get("extra", {})
        
        # Move custom fields to extra
        for key in ["video_id", "request_id", "extra_data"]:
            if key in kwargs:
                extra[key] = kwargs.pop(key)
                
        kwargs["extra"] = extra
        return msg, kwargs


def setup_logging(
    app_name: str = "swim-analytics",
    log_level: str = "INFO",
    log_dir: Path | None = None,
    json_format: bool = False,
) -> None:
    """
    Configure application-wide logging.
    
    Args:
        app_name: Name used for the root logger
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (None = console only)
        json_format: Use JSON formatting (for production)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter())
    
    root_logger.addHandler(console_handler)
    
    # File handler (if log_dir specified)
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler - 10MB max, keep 5 backups
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{app_name}.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())  # Always JSON for files
        root_logger.addHandler(file_handler)
        
        # Separate error log
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{app_name}.error.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)
    
    # Quiet noisy libraries
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)


def get_logger(name: str) -> ContextLogger:
    """
    Get a context-aware logger for a module.
    
    Usage:
        from app.utils.logging_config import get_logger
        logger = get_logger(__name__)
        
        logger.info("Starting process")
        logger.info("Processing video", video_id="abc123")
        logger.error("Failed", exc_info=True)
    """
    return ContextLogger(logging.getLogger(name), {})

