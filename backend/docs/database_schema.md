# MongoDB Collections

> All collections live inside the `swim_biomechanics` database (configurable via `MONGO_DB_NAME`).

## `videos`

Stores metadata about uploaded videos and overall pipeline status.

| Field        | Type     | Description                                      |
| ------------ | -------- | ------------------------------------------------ |
| `_id`        | string   | Primary key (`video_id`).                        |
| `path`       | string   | Absolute/relative path to the uploaded video.   |
| `status`     | string   | `pending`, `processing`, `processed`, `failed`.  |
| `uploaded_at`| datetime | UTC timestamp of upload.                         |
| `frame_rate` | float    | Detected frames per second.                      |
| `resolution` | object   | `{width, height}` of the source video.           |
| `notes`      | string   | Free-form analyst annotations.                   |

## `metrics`

Holds biomechanical metrics, stroke phases, and generated feedback.

| Field            | Type     | Description                                           |
| ---------------- | -------- | ----------------------------------------------------- |
| `_id`            | string   | Matches `video_id`.                                   |
| `metrics`        | object   | Numerical arrays and aggregated statistics.          |
| `stroke_phases`  | array    | List of `{phase_name, frame_indices}` objects.        |
| `narrative`      | object   | Generated feedback strings and contextual notes.      |
| `created_at`     | datetime | Timestamp when analytics were last generated.         |

## `frames`

Stores per-frame annotations and optional derived artifacts (e.g., overlays).

| Field        | Type     | Description                                             |
| ------------ | -------- | ------------------------------------------------------- |
| `_id`        | string   | Composite `video_id:frame_index`.                       |
| `video_id`   | string   | Parent video reference.                                 |
| `frame_index`| int      | Frame position inside the video.                        |
| `boxes`      | array    | List of YOLO bounding boxes `[x, y, w, h]`.             |
| `keypoints`  | array    | MediaPipe 33-keypoint array `[x, y, z, visibility]`.    |
| `artifacts`  | object   | Pointers to stored overlay images or debug assets.      |

## `reports`

Links generated reports with metadata for retrieval by the frontend.

| Field        | Type     | Description                                             |
| ------------ | -------- | ------------------------------------------------------- |
| `_id`        | string   | Matches `video_id`.                                     |
| `paths`      | object   | `{html: string, pdf: string}` file paths.               |
| `summary`    | string   | Short narrative summary for quick previews.             |
| `generated_at`| datetime| Timestamp for report generation.                         |

## Index Recommendations

- `videos.status` for monitoring queues.
- `metrics._id` (default) for fast lookup per video.
- Compound `{video_id: 1, frame_index: 1}` on `frames` for efficient frame scans.
- TTL index on debug artifacts if temporary storage is desired.


