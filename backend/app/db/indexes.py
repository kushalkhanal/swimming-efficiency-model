"""
Database index management for optimized queries.

This module creates indexes on frequently queried fields to improve query performance.
"""

from __future__ import annotations

from flask import current_app
from pymongo import IndexModel, ASCENDING, DESCENDING

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


def create_indexes() -> None:
    """
    Create indexes on all collections for optimal query performance.
    
    Should be called during application initialization.
    """
    db_name = current_app.config["MONGO_DB_NAME"]
    client = current_app.mongo  # type: ignore[attr-defined]
    db = client[db_name]
    
    # Videos collection indexes
    videos_collection = db["videos"]
    videos_indexes = [
        IndexModel([("_id", ASCENDING)]),  # Primary key (already exists, but explicit)
        IndexModel([("status", ASCENDING)]),  # For filtering by status
        IndexModel([("uploaded_at", DESCENDING)]),  # For sorting by upload date
    ]
    videos_collection.create_indexes(videos_indexes)
    logger.info("Created indexes on 'videos' collection")
    
    # Metrics collection indexes
    metrics_collection = db["metrics"]
    metrics_indexes = [
        IndexModel([("_id", ASCENDING)]),  # Primary key
        IndexModel([("created_at", DESCENDING)]),  # For sorting by creation date
    ]
    metrics_collection.create_indexes(metrics_indexes)
    logger.info("Created indexes on 'metrics' collection")
    
    # Frames collection indexes (most important for performance)
    frames_collection = db["frames"]
    frames_indexes = [
        IndexModel([("_id", ASCENDING)]),  # Primary key (composite: video_id:frame_index)
        IndexModel([("video_id", ASCENDING), ("frame_index", ASCENDING)]),  # Compound index for queries
        IndexModel([("video_id", ASCENDING)]),  # For filtering by video_id
        IndexModel([("frame_index", ASCENDING)]),  # For sorting by frame_index
    ]
    frames_collection.create_indexes(frames_indexes)
    logger.info("Created indexes on 'frames' collection")
    
    # Reports collection indexes
    reports_collection = db["reports"]
    reports_indexes = [
        IndexModel([("_id", ASCENDING)]),  # Primary key
    ]
    reports_collection.create_indexes(reports_indexes)
    logger.info("Created indexes on 'reports' collection")
    
    logger.info("Database indexes created successfully")


def ensure_indexes() -> None:
    """
    Ensure all indexes exist. Safe to call multiple times.
    """
    try:
        create_indexes()
    except Exception as e:
        logger.warning(f"Failed to create indexes (they may already exist): {e}")

