"""
MongoDB client initialization.
"""

from __future__ import annotations

from typing import Any, Mapping

from pymongo import MongoClient


def init_mongo(config: Mapping[str, Any]) -> MongoClient:
    """
    Create a MongoDB client using the provided configuration mapping.
    """
    uri: str = config["MONGO_URI"]
    client = MongoClient(uri, tz_aware=True)
    return client

