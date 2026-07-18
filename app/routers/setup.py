from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.core.templates import templates

router = APIRouter()

@router.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="setup.html",
        context={
            "title": "GarminSupla - Setup",
        },
    )
