"""
Repository helpers providing a thin layer over MongoDB collections.
"""
from __future__ import annotations
from dataclasses import asdict

from typing import Any, Iterable

from flask import current_app

from ..services.pose_estimation import Pose2DResult
from ..services.detection import DetectedFrame


class BaseRepository:
    """
    Provides convenience accessors for MongoDB collections.
    """

    collection_name: str

    @property
    def collection(self):
        db_name = current_app.config["MONGO_DB_NAME"]
        client = current_app.mongo  # type: ignore[attr-defined]
        return client[db_name][self.collection_name]


class VideoRepository(BaseRepository):
    collection_name = "videos"

    def insert_video(self, video_id: str, metadata: dict[str, Any]) -> None:
        self.collection.insert_one({"_id": video_id, **metadata})

    def fetch_video(self, video_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"_id": video_id})

    def update_status(self, video_id: str, *, status: str) -> None:
        self.collection.update_one({"_id": video_id}, {"$set": {"status": status}})


class MetricsRepository(BaseRepository):
    collection_name = "metrics"

    def store_metrics(
        self,
        video_id: str,
        *,
        metrics: dict[str, Any],
        stroke_phases: Iterable[Any],
        narrative: dict[str, Any],
    ) -> None:
        doc = {
            "_id": video_id,
            "metrics": metrics,
            "stroke_phases": [asdict(phase) for phase in stroke_phases],
            "narrative": narrative,
        }
        self.collection.replace_one({"_id": video_id}, doc, upsert=True)

    def fetch_metrics(self, video_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"_id": video_id}, {"_id": False})


class FrameRepository(BaseRepository):
    collection_name = "frames"

    def store_frames(
        self, video_id: str, frames: Iterable[DetectedFrame], poses: Iterable[Pose2DResult]
    ) -> None:
        pose_map = {int(pose.frame_index): pose.keypoints.tolist() for pose in poses}
        docs = []
        for frame in frames:
            frame_idx = int(frame.frame_index)  # Convert numpy.int32 to Python int
            # Convert boxes tuples to lists of native Python ints
            boxes = [[int(x) for x in box] for box in frame.boxes]
            docs.append(
                {
                    "_id": f"{video_id}:{frame_idx}",
                    "video_id": video_id,
                    "frame_index": frame_idx,
                    "boxes": boxes,
                    "keypoints": pose_map.get(frame_idx, []),
                }
            )
        if docs:
            self.collection.insert_many(docs, ordered=False)

    def fetch_frame(self, frame_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"_id": frame_id}, {"_id": False})


class ReportRepository(BaseRepository):
    collection_name = "reports"

    def upsert_report(self, video_id: str, paths: dict[str, str]) -> None:
        doc = {
            "_id": video_id,
            "paths": paths,
        }
        self.collection.replace_one({"_id": video_id}, doc, upsert=True)

    def fetch_paths(self, video_id: str) -> dict[str, str] | None:
        doc = self.collection.find_one({"_id": video_id})
        if not doc:
            return None
        return doc.get("paths")

