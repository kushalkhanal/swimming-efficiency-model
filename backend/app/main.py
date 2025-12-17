"""
Command-line entry point for running the Flask development server.
"""

from __future__ import annotations

import argparse

from . import create_app, get_socketio


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start the offline biomechanical analytics backend.",
    )
    parser.add_argument(
        "--config",
        default="OFFLINE_DEV",
        help="Configuration profile to load (default: OFFLINE_DEV)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host interface for the Flask development server.",
    )
    parser.add_argument(
        "--port",
        default=8000,
        type=int,
        help="Port for the Flask development server.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app = create_app(args.config)
    socketio = get_socketio()
    # Use debug=False on Windows to avoid socket errors with threading mode
    socketio.run(app, host=args.host, port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()

