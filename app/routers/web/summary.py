from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/summary", response_class=HTMLResponse)
async def summary(request: Request):
    return templates.TemplateResponse(
        "summary.html",
        {
            "request": request,
            "step": 4,
            "steps": 4,
        },
    )
