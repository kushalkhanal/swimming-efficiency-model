"""
Helpers for offline file storage and organization.
"""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO


def save_upload(file_storage: BinaryIO, target_path: Path) -> Path:
    """
    Persist an uploaded file stream to disk and return the path.
    """
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with open(target_path, "wb") as destination:
        destination.write(file_storage.read())

    return target_path

