from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/select-gate", response_class=HTMLResponse)
async def select_gate(request: Request):
    return templates.TemplateResponse(
        "select_gate.html",
        {
            "request": request,
             "step": 3,
             "steps": 4,
        },
    )
