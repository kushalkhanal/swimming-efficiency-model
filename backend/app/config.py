"""
Configuration profiles for offline environments.

The project is designed to run without any external network access so all
connections use loopback addresses or local file paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Type


@dataclass(slots=True)
class BaseConfig:
    """Baseline settings shared across environments."""

    DEBUG: bool = False
    TESTING: bool = False
    SECRET_KEY: str = "offline-secret-key"
    UPLOAD_ROOT: Path = field(default_factory=lambda: Path("./data/uploads"))
    ARTIFACT_ROOT: Path = field(default_factory=lambda: Path("./data/artifacts"))
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "swim_biomechanics"
    CORS_ORIGINS: list[str] = field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ]
    )

    @property
    def upload_root(self) -> Path:
        self.UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
        return self.UPLOAD_ROOT

    @property
    def artifact_root(self) -> Path:
        self.ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
        return self.ARTIFACT_ROOT


@dataclass(slots=True)
class OfflineDevConfig(BaseConfig):
    """Default configuration used for local development."""

    DEBUG: bool = True


@dataclass(slots=True)
class OfflineTestConfig(BaseConfig):
    """Configuration used for automated testing."""

    TESTING: bool = True
    MONGO_DB_NAME: str = "swim_biomechanics_test"


CONFIG_MAP: dict[str, Type[BaseConfig]] = {
    "OFFLINE_DEV": OfflineDevConfig,
    "OFFLINE_TEST": OfflineTestConfig,
}


def get_config(name: str | None) -> BaseConfig:
    """
    Resolve the configuration dataclass for the provided name.

    Defaults to `OfflineDevConfig` when `name` is missing or unknown.
    """
    config_cls = CONFIG_MAP.get((name or "").upper(), OfflineDevConfig)
    return config_cls()

