"""CLI for serving the TRACE FastAPI backend."""

from __future__ import annotations

import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the TRACE FastAPI backend.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface to bind.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind.")
    parser.add_argument("--reload", action="store_true", help="Enable autoreload for development.")
    args = parser.parse_args()

    uvicorn.run(
        "trace_backend.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
