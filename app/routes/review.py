"""
Review routes -- HTTP layer only, delegates to business logic.

Performance design:
  GET /             -- serves HTML skeleton INSTANTLY (no LLM wait).
                       JS fetches the review from /api/review after DOM load.
  GET /api/review   -- pops from ReviewPool (sub-ms if warm) or generates live.
  GET /favicon.*    -- 301 redirects to static assets.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.core.review_generator import review_pool


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# -- Favicon redirects -- browsers hard-fetch /favicon.* from root ------------

@router.get("/favicon.ico", include_in_schema=False)
async def favicon_ico():
    return RedirectResponse(url="/static/favicon.ico", status_code=301)


@router.get("/favicon.png", include_in_schema=False)
async def favicon_png():
    return RedirectResponse(url="/static/favicon.png", status_code=301)


# -- Main page -- serves skeleton HTML instantly, JS loads review async --------

@router.get("/", response_class=HTMLResponse)
async def review_page(request: Request):
    """
    Renders the page skeleton immediately -- no LLM call here.
    The review text is loaded client-side via /api/review after DOM ready.
    Page appears in <100ms; review fills in ~2-3s in the background.
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


# -- API endpoint -- pops from pool (instant if warm) -------------------------

@router.get("/api/review", response_class=JSONResponse)
async def api_generate_review():
    """
    Returns a fresh review as JSON.
    Pops from ReviewPool (sub-millisecond if pool is warm).
    Pool triggers background refill after each pop.
    Falls back to live generation if pool is empty.
    """
    settings = get_settings()

    try:
        review_text = await review_pool.get()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )

    return {
        "review":            review_text,
        "google_review_url": settings.google_review_url,
    }
