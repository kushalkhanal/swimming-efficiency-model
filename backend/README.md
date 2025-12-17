## Backend Overview

This backend is a Flask-based service that runs fully offline and provides computer vision powered biomechanical analysis for swimming videos.

### Key Features

- Accepts raw swimming videos through REST endpoints.
- Performs detection, pose estimation, and biomechanical analytics using open-source libraries (YOLOv8, MediaPipe Pose, optional VideoPose3D).
- Stores structured results in MongoDB for quick retrieval by the frontend.
- Generates data and assets for reports (JSON, annotated frames, and summary narratives).

### Directory Layout

```
backend/
  app/
    __init__.py           # Application factory that wires config, DB, and blueprints
    config.py             # Offline-safe configuration settings
    main.py               # CLI entry point for running the development server
    routes/               # Flask blueprints exposing the REST API
    services/             # Computer vision and analytics processing pipelines
    models/               # Dataclasses/Pydantic models for typed data interchange
    db/                   # MongoDB connection helpers and collection accessors
    utils/                # Cross-cutting utilities (storage, validation, logging)
  tests/                  # Placeholder for future unit/integration tests
  docs/                   # Architectural notes and schema descriptions
```

Run `python -m app.main` to start the development server once dependencies are installed and MongoDB is available.

