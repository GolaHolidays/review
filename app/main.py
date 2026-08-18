"""
FastAPI application factory -- wires everything together.

Performance:
  - GZipMiddleware compresses all text responses >= 1KB automatically
  - lifespan warms the ReviewPool at startup so first request is instant
  - StaticFiles uses an absolute path (required in Vercel serverless env)
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes.review import router as review_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    Startup: warm the review pool so the very first visitor gets a fast response.
    Shutdown: nothing to clean up (pool tasks are daemon-like).
    """
    from app.core.review_generator import review_pool
    await review_pool.warmup()
    yield


def create_app() -> FastAPI:
    """Application factory -- creates and configures the FastAPI app."""
    settings = get_settings()

    application = FastAPI(
        title=f"{settings.brand_name} -- Review System",
        description="AI-powered Google review generator",
        version="1.0.0",
        docs_url="/docs" if settings.app_debug else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    # GZip: automatically compresses HTML/JSON/CSS responses >= 1KB
    # Reduces transfer size ~70% for text payloads
    application.add_middleware(GZipMiddleware, minimum_size=1000)

    # Mount static files -- absolute path ensures correct resolution in Vercel
    _static_dir = Path(__file__).resolve().parent.parent / "static"
    application.mount("/static", StaticFiles(directory=_static_dir), name="static")

    # Register routes
    application.include_router(review_router)

    return application


app = create_app()
