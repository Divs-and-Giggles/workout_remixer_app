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
from app.models import Workout, RoutineWorkout
from datetime import date 
from sqlmodel import select

from sqlalchemy import or_
from fastapi.responses import HTMLResponse
from sqlmodel import select

@router.get("/routines", response_class=HTMLResponse)
async def routine_view(request: Request, user: AuthDep, session: SessionDep):

    my_routines = session.exec(
        select(Routine).where(
            Routine.user_id == user.id,
            or_(Routine.is_system == False, Routine.is_system == None),
            or_(Routine.is_remix == False, Routine.is_remix == None)
        )
    ).all()

    our_routines = session.exec(
        select(Routine).where(Routine.is_system == True)
    ).all()

    generated_routines = session.exec(
        select(Routine).where(
            Routine.user_id == user.id,
            Routine.is_remix == True
        )
    ).all()

    workouts = session.exec(select(Workout)).all()

    return templates.TemplateResponse(
        request=request,
        name="routine.html",
        context={
            "request": request,
            "user": user,
            "my_routines": my_routines,
            "our_routines": our_routines,
            "generated_routines": generated_routines,
            "workouts": workouts
        }
    )

@router.post("/routines")
async def create_routine(
    user: AuthDep,
    session: SessionDep,
    payload: dict = Body(...)
):

    workouts = payload.get("workouts", [])

    routine = Routine(
        name=payload["name"],
        user_id=user.id,
        is_system=False,
        is_remix=False
    )

    session.add(routine)
    session.commit()
    session.refresh(routine)

    for i, w in enumerate(workouts):
        session.add(RoutineWorkout(
            routine_id=routine.id,
            workout_id=w["id"],
            difficulty=w.get("difficulty", "beginner"),
            sets=w.get("sets", 3),
            reps=w.get("reps", 10),
            order_in_routine=i
        ))

    session.commit()

    return {"ok": True, "id": routine.id}

@router.post("/routines/{routine_id}/remix")
def remix_routine(routine_id: int, user: AuthDep, session: SessionDep):

    original = session.get(Routine, routine_id)

    if not original:
        raise HTTPException(status_code=404)

    if not original.is_system:
        raise HTTPException(status_code=403, detail="Only system routines can be remixed")

    new_routine = Routine(
        name=f"{original.name} (Remix)",
        user_id=user.id,
        is_system=False,
        is_remix=True
    )

    session.add(new_routine)
    session.commit()
    session.refresh(new_routine)

    links = session.exec(
        select(RoutineWorkout).where(RoutineWorkout.routine_id == routine_id)
    ).all()

    for i, l in enumerate(links):
        session.add(RoutineWorkout(
            routine_id=new_routine.id,
            workout_id=l.workout_id,
            sets=l.sets or 3,
            reps=l.reps or 10,
            difficulty=l.difficulty,
            order_in_routine=i
        ))

    session.commit()

    return {"ok": True}

@router.delete("/routines/{routine_id}")
def delete_routine(routine_id: int, user: AuthDep, session: SessionDep):

    routine = session.get(Routine, routine_id)

    if not routine:
        raise HTTPException(status_code=404)

    if routine.is_system:
        raise HTTPException(status_code=403, detail="Cannot delete system routines")

    if routine.user_id != user.id:
        raise HTTPException(status_code=403)

    session.delete(routine)
    session.commit()

    return {"ok": True}