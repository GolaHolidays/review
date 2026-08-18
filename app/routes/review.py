"""
Review routes — HTTP layer only, delegates to business logic.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.core.review_generator import generate_review


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates",
)


@router.get("/", response_class=HTMLResponse)
async def review_page(request: Request):
    """
    Main page — generates an AI review and renders the template.
    """
    settings = get_settings()

    try:
        review_text = generate_review()
    except Exception as e:
        review_text = f"Unable to generate review. Please refresh the page. ({e})"

    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={
            "brand_name": settings.brand_name,
            "brand_tagline": settings.brand_tagline,
            "review_text": review_text,
            "google_review_url": settings.google_review_url,
        },
    )


@router.get("/api/review", response_class=JSONResponse)
async def api_generate_review():
    """
    API endpoint — returns a fresh review as JSON.
    Useful for regenerating without full page reload.
    """
    settings = get_settings()

    try:
        review_text = generate_review()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )

    return {
        "review": review_text,
        "google_review_url": settings.google_review_url,
    }
