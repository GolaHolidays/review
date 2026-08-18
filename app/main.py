"""
FastAPI application factory — wires everything together.
"""

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

    # Mount static files
    application.mount("/static", StaticFiles(directory="static"), name="static")

    # Register routes
    application.include_router(review_router)

    return application


app = create_app()
