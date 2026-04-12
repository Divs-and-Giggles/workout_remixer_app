from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form, APIRouter, HTTPException, Body
from app.dependencies import SessionDep, AuthDep
from . import router, templates
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from app.config import get_settings
from fastapi.responses import HTMLResponse
from app.models.routine import Routine, RoutineCreate, RoutineUpdate
from datetime import date
from sqlmodel import select

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
            "user": user,
            "routines": routines   
        }
    )
@router.post("/routines")
def create_routine(
    user: AuthDep,
    session: SessionDep,
    payload: dict = Body(...)
):

    routine = Routine(
        name=payload["name"],
        difficulty=payload.get("difficulty", "beginner"),
        is_generated=payload.get("is_generated", False),
        creation_date=date.today(),
        user_id=user.id
    )

    session.add(routine)
    session.commit()
    session.refresh(routine)

    return routine

# UPDATE ROUTINE

@router.put("/routines/{id}")
def update_routine(
    id: int,
    user: AuthDep,
    session: SessionDep,
    payload: dict = Body(...)
):

    routine = session.get(Routine, id)

    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=404, detail="Routine not found")

    if "name" in payload:
        routine.name = payload["name"]

    if "difficulty" in payload:
        routine.difficulty = payload["difficulty"]

    if "is_generated" in payload:
        routine.is_generated = payload["is_generated"]

    session.add(routine)
    session.commit()

    return {"message": "updated"}

# DELETE ROUTINE

@router.delete("/routines/{id}")
def delete_routine(
    id: int,
    user: AuthDep,
    session: SessionDep
):

    routine = session.get(Routine, id)

    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=404, detail="Routine not found")

    session.delete(routine)
    session.commit()

    return {"message": "deleted"}

# REMIX ROUTINE

@router.post("/routines/{id}/remix")
def remix_routine(
    id: int,
    user: AuthDep,
    session: SessionDep
):

    routine = session.get(Routine, id)

    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    new_routine = Routine(
        name=f"{routine.name} (Remix)",
        difficulty=routine.difficulty,
        is_generated=True,
        creation_date=date.today(),
        user_id=user.id
    )

    session.add(new_routine)
    session.commit()
    session.refresh(new_routine)

    return new_routine