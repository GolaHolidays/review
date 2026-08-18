"""
Review routes -- HTTP layer only, delegates to business logic.

Performance:
  GET /           -- serves self-contained HTML instantly (ALL CSS inlined).
                     Zero external requests needed to render.
                     JS fetches review from /api/review after paint.
  GET /api/review -- single async LLM call, returns JSON.
  GET /favicon.*  -- 301 redirects to static assets.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.core.review_generator import agenerate_review


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# -- Favicon redirects --------------------------------------------------------

@router.get("/favicon.ico", include_in_schema=False)
async def favicon_ico():
    return RedirectResponse(url="/static/favicon.ico", status_code=301)


@router.get("/favicon.png", include_in_schema=False)
async def favicon_png():
    return RedirectResponse(url="/static/favicon.png", status_code=301)


# -- Main page ----------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
async def review_page(request: Request):
    """
    Serves the complete page instantly. All CSS is inlined in the template,
    so the browser can paint immediately with zero additional requests.
    Review text loads async via /api/review.
    """
    settings = get_settings()
    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={
            "brand_name":        settings.brand_name,
            "brand_tagline":     settings.brand_tagline,
            "google_review_url": settings.google_review_url,
        },
    )


# -- API: single async LLM call per request ----------------------------------

@router.get("/api/review", response_class=JSONResponse)
async def api_generate_review():
    """
    Returns a fresh review as JSON. Single async LLM call.
    No pool, no warmup -- optimal for serverless (Vercel).
    """
    settings = get_settings()

    try:
        review_text = await agenerate_review()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )

    return {
        "review":            review_text,
        "google_review_url": settings.google_review_url,
    }
