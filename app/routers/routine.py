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
      routines = session.exec( select(Routine).where(Routine.user_id == user.id) ).all() 
      return templates.TemplateResponse(
           request=request, 
           name="routine.html",
           context={ "user": user,
           "routines": routines 
    } )

# =========================
# CREATE ROUTINE
# =========================
@router.post("/routines")
def create_routine(
    user: AuthDep,
    session: SessionDep,
    payload: dict = Body(...)
):

    routine = Routine(
        name=payload["name"],
        difficulty=payload.get("difficulty", "beginner"),
        user_id=user.id,
        is_system=False,
        creation_date=date.today()
    )

    session.add(routine)
    session.commit()
    session.refresh(routine)

    return routine


# =========================
# UPDATE ROUTINE
# =========================
@router.put("/routines/{id}")
def update_routine(id: int, data: RoutineUpdate, user: AuthDep, session: SessionDep):

    routine = session.get(Routine, id)

    if not routine:
        raise HTTPException(404, "Routine not found")

    # 🚫 SYSTEM ROUTINES BLOCKED
    if routine.is_system:
        raise HTTPException(403, "System routines cannot be edited")

    if routine.user_id != user.id:
        raise HTTPException(403, "Not allowed")

    if data.name is not None:
        routine.name = data.name

    if data.difficulty is not None:
        routine.difficulty = data.difficulty

    session.add(routine)
    session.commit()
    session.refresh(routine)

    return routine


# =========================
# DELETE ROUTINE
# =========================
@router.delete("/routines/{id}")
def delete_routine(id: int, user: AuthDep, session: SessionDep):

    routine = session.get(Routine, id)

    if not routine:
        raise HTTPException(404, "Routine not found")

    # 🚫 SYSTEM ROUTINES CANNOT BE DELETED
    if routine.is_system:
        raise HTTPException(403, "System routines cannot be deleted")

    if routine.user_id != user.id:
        raise HTTPException(403, "Not allowed")

    session.delete(routine)
    session.commit()

    return {"message": "deleted"}


# =========================
# REMIX ROUTINE (CORE FEATURE)
# =========================
@router.post("/routines/{id}/remix")
def remix_routine(id: int, user: AuthDep, session: SessionDep):

    base = session.get(Routine, id)

    if not base:
        raise HTTPException(404, "Routine not found")

    new_routine = Routine(
        name=f"{base.name} (Remix)",
        difficulty=base.difficulty,
        user_id=user.id,
        is_system=False,
        creation_date=date.today()
    )

    session.add(new_routine)
    session.commit()
    session.refresh(new_routine)

    return new_routine