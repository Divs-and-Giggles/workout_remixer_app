from fastapi.responses import HTMLResponse
from sqlmodel import select
from datetime import date
from app.dependencies import SessionDep, AuthDep
from app.models import Routine, RoutineWorkout, Workout
from . import templates, router
from fastapi import Request,Body

@router.get("/routines", response_class=HTMLResponse)
async def routine_view(request: Request, user: AuthDep, session: SessionDep):

   my_routines = session.exec(select(Routine).where( Routine.user_id == user.id, Routine.is_generated == False)).all()
   
   our_routines = session.exec(select(Routine).where(Routine.user_id != user.id, Routine.is_generated == False)).all()
   
   workouts = session.exec(select(Workout)).all()

   generated_routines = session.exec(select(Routine).where(Routine.user_id == user.id, Routine.is_generated == True)).all()

   
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
