from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.setup_service import SetupService

router = APIRouter()

templates = Jinja2Templates(directory="templates")

setup_service = SetupService()


@router.get("/select-gate", response_class=HTMLResponse)
async def select_gate(request: Request):

    status = setup_service.get_status()

    if not status.authorized:
        return RedirectResponse(
            url="/setup",
            status_code=303,
        )

    return templates.TemplateResponse(
        "select_gate.html",
        {
            "request": request,
             "step": 3,
             "steps": 4,
        },
    )
