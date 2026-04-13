from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form, APIRouter, HTTPException, Body
from app.dependencies import SessionDep, AuthDep
from . import router, templates
from typing import Annotated, Optional
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from app.config import get_settings
from fastapi.responses import HTMLResponse
from app.models.routine import Routine, RoutineCreate, RoutineUpdate, RoutineWorkout, Workout
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

@router.post("/routines/{routine_id}/workouts")
def add_workout_to_routine(
    request: Request,
    routine_id: int,
    user: AuthDep,
    session: SessionDep,
    workout_id: Annotated[int, Form()],
    sets: Annotated[int, Form()],
    difficulty: Annotated[str, Form()],
    reps: Annotated[Optional[int], Form()] = None,
    duration_seconds: Annotated[Optional[int], Form()] = None,
    is_warmup: Annotated[bool, Form()] = False,
    is_cooldown: Annotated[bool, Form()] = False,
):
    routine = session.get(Routine, routine_id)
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=404, detail="Routine not found")

    workout = session.get(Workout, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    existing = session.exec(
        select(RoutineWorkout).where(RoutineWorkout.routine_id == routine_id)
    ).all()
    next_order = len(existing) + 1

    routine_workout = RoutineWorkout(
        routine_id=routine_id,
        workout_id=workout_id,
        difficulty=difficulty,
        order_in_routine=next_order,
        sets=sets,
        reps=reps,
        duration_seconds=duration_seconds,
        is_warmup=is_warmup,
        is_cooldown=is_cooldown,
    )

    session.add(routine_workout)
    session.commit()
    session.refresh(routine_workout)
    flash(request, f"Workout Added!", "success")

    return routine_workout


@router.delete("/routines/{routine_id}/workouts/{workout_id}")
def remove_workout_from_routine(
    routine_id: int,
    workout_id: int,
    user: AuthDep,
    session: SessionDep,
):
    routine = session.get(Routine, routine_id)
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=404, detail="Routine not found")

    routine_workout = session.get(RoutineWorkout, (routine_id, workout_id))
    if not routine_workout:
        raise HTTPException(status_code=404, detail="RoutineWorkout not found")

    session.delete(routine_workout)
    session.commit()

    return {"message": "Workout removed from routine"}
