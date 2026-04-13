from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form, APIRouter, HTTPException, Body
<<<<<<< HEAD
from app.dependencies import SessionDep, AuthDep 
from . import router, templates
from app.services.auth_service import AuthService 
=======
from app.dependencies import SessionDep, AuthDep
from . import router, templates
from typing import Annotated, Optional
from app.services.auth_service import AuthService
>>>>>>> 7ca3752f48531a8fb5ddf87ec194801f9617c11c
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from app.config import get_settings
<<<<<<< HEAD
from fastapi.responses import HTMLResponse 
from app.models.routine import Routine, RoutineCreate, RoutineUpdate
from app.models import Workout, RoutineWorkout
from datetime import date 
from sqlmodel import select

@router.get("/routines", response_class=HTMLResponse)
async def routine_view(request: Request, user: AuthDep, session: SessionDep):

   my_routines = session.exec(
    select(Routine).where(
        Routine.user_id == user.id,
        Routine.is_system == False,
        Routine.is_remix == False
    )
).all()
   
   our_routines = session.exec(
        select(Routine).where(Routine.is_system == True)
    ).all()
   
   workouts = session.exec(select(Workout)).all()

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
        "request" : request,
        "user": user,
        "my_routines": my_routines,
        "our_routines": our_routines,
        "workouts": workouts,
        "generated_routines": generated_routines
    }

)
=======
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
>>>>>>> 7ca3752f48531a8fb5ddf87ec194801f9617c11c

@router.post("/routines")
async def create_routine(
    user: AuthDep,
    session: SessionDep,
    payload: dict = Body(...)
):

    workouts = payload.get("workouts", [])

    routine = Routine(
        name=payload["name"],
<<<<<<< HEAD
        user_id=user.id,
        is_system=False,
        is_generated=False,
        is_remix=False
=======
        difficulty=payload.get("difficulty", "beginner"),
        is_generated=payload.get("is_generated", False),
        creation_date=date.today(),
        user_id=user.id
>>>>>>> 7ca3752f48531a8fb5ddf87ec194801f9617c11c
    )

    session.add(routine)
    session.commit()
    session.refresh(routine)

    for i, w in enumerate(workouts):
        link = RoutineWorkout(
            routine_id=routine.id,
            workout_id=w["id"],
            difficulty=w.get("difficulty", "beginner"),
            sets=w.get("sets", 3),
            reps=w.get("reps", 10),
            order_in_routine=i
        )
        session.add(link)   # ✅ IMPORTANT FIX

    session.commit()

    return {"ok": True, "id": routine.id}


# =========================
# GET SINGLE ROUTINE (FOR MODAL)
# =========================
@router.get("/routines/{routine_id}")
def get_routine(routine_id: int, user: AuthDep, session: SessionDep):

    routine = session.get(Routine, routine_id)

    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    if routine.user_id != user.id and not routine.is_system:
        raise HTTPException(status_code=403, detail="Not allowed")

    links = session.exec(
        select(RoutineWorkout).where(RoutineWorkout.routine_id == routine_id)
    ).all()

    workouts = []

    for l in links:
        workout = session.get(Workout, l.workout_id)

        workouts.append({
            "id": l.workout_id,
            "name": workout.name if workout else "Workout",
            "sets": l.sets or 3,
            "reps": l.reps or 10,
            "order": l.order_in_routine or 0
        })

    return {
        "id": routine.id,
        "name": routine.name,
        "workouts": sorted(workouts, key=lambda x: x["order"])
    }


# =========================
# EDIT PAGE
# =========================
@router.get("/routines/{routine_id}/edit", response_class=HTMLResponse)
async def edit_routine(
    routine_id: int,
    request: Request,
    session: SessionDep,
    user: AuthDep
):

    routine = session.get(Routine, routine_id)

    if not routine:
        raise HTTPException(status_code=404)

    if routine.user_id != user.id:
        raise HTTPException(status_code=403)

    workouts = session.exec(select(Workout)).all()

    links = session.exec(
        select(RoutineWorkout).where(RoutineWorkout.routine_id == routine_id)
    ).all()

    selected = {l.workout_id for l in links}

    return templates.TemplateResponse(
        "edit_routine.html",
        {
            "request": request,
            "routine": routine,
            "workouts": workouts,
            "selected": selected
        }
    )

# UPDATE ROUTINE

@router.put("/routines/{id}")
def update_routine(
    id: int,
    user: AuthDep,
    session: SessionDep,
    payload: dict = Body(...)
):

    routine = session.get(Routine, id)

<<<<<<< HEAD
    if not routine:
        raise HTTPException(status_code=404)

    if routine.is_system:
        raise HTTPException(status_code=403, detail="Cannot edit system routines")

    if routine.user_id != user.id:
        raise HTTPException(status_code=403)

    if data.name:
        routine.name = data.name

    if data.difficulty:
        routine.difficulty = data.difficulty
=======
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=404, detail="Routine not found")

    if "name" in payload:
        routine.name = payload["name"]

    if "difficulty" in payload:
        routine.difficulty = payload["difficulty"]

    if "is_generated" in payload:
        routine.is_generated = payload["is_generated"]
>>>>>>> 7ca3752f48531a8fb5ddf87ec194801f9617c11c

    session.add(routine)
    session.commit()

<<<<<<< HEAD
    return {"ok": True}
=======
    return {"message": "updated"}
>>>>>>> 7ca3752f48531a8fb5ddf87ec194801f9617c11c

# DELETE ROUTINE
<<<<<<< HEAD
# =========================
@router.delete("/routines/{routine_id}")
def delete_routine(routine_id: int, user: AuthDep, session: SessionDep):
=======

@router.delete("/routines/{id}")
def delete_routine(
    id: int,
    user: AuthDep,
    session: SessionDep
):
>>>>>>> 7ca3752f48531a8fb5ddf87ec194801f9617c11c

    routine = session.get(Routine, routine_id)

<<<<<<< HEAD
    if not routine:
        raise HTTPException(status_code=404)

    if routine.user_id != user.id:
        raise HTTPException(status_code=403)
=======
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=404, detail="Routine not found")
>>>>>>> 7ca3752f48531a8fb5ddf87ec194801f9617c11c

    session.delete(routine)
    session.commit()

    return {"ok": True}

# REMIX ROUTINE

<<<<<<< HEAD
# =========================
# REMIX ROUTINE
# =========================
@router.post("/routines/{routine_id}/remix")
def remix_routine(routine_id: int, user: AuthDep, session: SessionDep):

    original = session.get(Routine, routine_id)

    if not original:
        raise HTTPException(status_code=404)

    new_routine = Routine(
        name=f"{original.name} (Remix)",
        user_id=user.id,
        is_system=False,
        is_remix=True,
        is_generated=False
=======
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
>>>>>>> 7ca3752f48531a8fb5ddf87ec194801f9617c11c
    )

    session.add(new_routine)
    session.commit()
    session.refresh(new_routine)

<<<<<<< HEAD
    links = session.exec(
        select(RoutineWorkout).where(RoutineWorkout.routine_id == routine_id)
    ).all()

    for i, l in enumerate(links):
        session.add(RoutineWorkout(
            routine_id=new_routine.id,
            workout_id=l.workout_id,
            sets=l.sets or 3,
            reps=l.reps or 10,
            order_in_routine=i
        ))

    session.commit()

    return {"ok": True}
=======
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
>>>>>>> 7ca3752f48531a8fb5ddf87ec194801f9617c11c
