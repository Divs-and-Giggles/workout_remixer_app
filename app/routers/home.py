from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form, APIRouter
from app.dependencies import SessionDep, AuthDep
from . import router, templates
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from app.config import get_settings


@router.get("/home", response_class=HTMLResponse)
async def home_view(request:Request, user:AuthDep):
    return templates.TemplateResponse(
          request=request, 
          name="home.html",
          context={"user":user}
    )
