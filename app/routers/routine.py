from fastapi.responses import HTMLResponse
from sqlmodel import select
from datetime import date
from app.dependencies import SessionDep, AuthDep
from app.models import Routine, RoutineWorkout, Workout
from . import templates, router
from fastapi import Request

@router.get("/routines", response_class=HTMLResponse)
async def routine_view(
    request: Request,
    user: AuthDep,
    session: SessionDep
):

    routines = session.exec(
        select(Routine).where(Routine.user_id == user.id)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="routine.html",
        context={
            "request": request,
            "user": user,
            "routines": routines
        }
    )  