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
        is_generated=False,
        is_remix=False
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
        session.add(link)  

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


# =========================
# UPDATE ROUTINE
# =========================
@router.put("/routines/{id}")
def update_routine(id: int, data: RoutineUpdate, user: AuthDep, session: SessionDep):

    routine = session.get(Routine, id)

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

    session.add(routine)
    session.commit()

    return {"ok": True}


# =========================
# DELETE ROUTINE
# =========================
@router.delete("/routines/{routine_id}")
def delete_routine(routine_id: int, user: AuthDep, session: SessionDep):

    routine = session.get(Routine, routine_id)

    if not routine:
        raise HTTPException(status_code=404)

    if routine.user_id != user.id:
        raise HTTPException(status_code=403)

    session.delete(routine)
    session.commit()

    return {"ok": True}


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
            order_in_routine=i
        ))

    session.commit()

    return {"ok": True}
