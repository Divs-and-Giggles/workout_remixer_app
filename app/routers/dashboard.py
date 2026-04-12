from fastapi.responses import RedirectResponse
from fastapi import Request, status
from app.dependencies.auth import IsUserLoggedIn, get_current_user, is_admin
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from . import router,templates
from app.models.logging import WaterIntake
from datetime import datetime, date
from sqlmodel import select

@router.get("/dashboard")
def water_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name="dashboard.html"
        )