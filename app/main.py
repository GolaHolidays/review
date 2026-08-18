"""
FastAPI application factory — wires everything together.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes.review import router as review_router


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI app."""
    settings = get_settings()

    application = FastAPI(
        title=f"{settings.brand_name} — Review System",
        description="AI-powered Google review generator",
        version="1.0.0",
        docs_url="/docs" if settings.app_debug else None,
        redoc_url=None,
    )

    # Mount static files — absolute path ensures correct resolution in Vercel
    _static_dir = Path(__file__).resolve().parent.parent / "static"
    application.mount("/static", StaticFiles(directory=_static_dir), name="static")

    # Register routes
    application.include_router(review_router)

    return application


app = create_app()
