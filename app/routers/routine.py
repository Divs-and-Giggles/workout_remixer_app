from fastapi.responses import HTMLResponse
from sqlmodel import select
from datetime import date
from app.dependencies import SessionDep, AuthDep
from app.models import Routine, RoutineWorkout, Workout
from . import templates, router
from fastapi import Request, Body, Form, HTTPException, Query
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from typing import Annotated, Optional
from app.pagination import Pagination

ROUTINES_PER_PAGE = 8

def flash(request: Request, message: str, category: str = "info"):
    """Store a flash message in the session"""
    if "messages" not in request.session:
        request.session["messages"] = []
    request.session["messages"].append({"message": message, "category": category})

@router.get("/routines", response_class=HTMLResponse)
async def routine_view(
    request: Request,
    user: AuthDep,
    session: SessionDep,
    my_page: int = Query(1, ge=1),
    our_page: int = Query(1, ge=1),
    gen_page: int = Query(1, ge=1),
):
    limit = ROUTINES_PER_PAGE

    all_my = session.exec(select(Routine).where(Routine.user_id == user.id, Routine.is_generated == False)).all()
    all_our = session.exec(select(Routine).where(Routine.user_id != user.id, Routine.is_generated == False)).all()
    all_gen = session.exec(select(Routine).where(Routine.user_id == None, Routine.is_generated == True)).all()

    my_pagination = Pagination(total_count=len(all_my), current_page=my_page, limit=limit)
    our_pagination = Pagination(total_count=len(all_our), current_page=our_page, limit=limit)
    gen_pagination = Pagination(total_count=len(all_gen), current_page=gen_page, limit=limit)

    my_routines = all_my[(my_page - 1) * limit: my_page * limit]
    our_routines = all_our[(our_page - 1) * limit: our_page * limit]
    generated_routines = all_gen[(gen_page - 1) * limit: gen_page * limit]

    workouts = session.exec(select(Workout)).all()

    return templates.TemplateResponse(
        request=request,
        name="routine.html",
        context={
            "request": request,
            "user": user,
            "my_routines": my_routines,
            "our_routines": our_routines,
            "workouts": workouts,
            "generated_routines": generated_routines,
            "my_pagination": my_pagination,
            "our_pagination": our_pagination,
            "gen_pagination": gen_pagination,
            "my_page": my_page,
            "our_page": our_page,
            "gen_page": gen_page,
        }
    )

@router.post("/routines")
async def create_routine(
    request: Request,    
    user: AuthDep,
    session: SessionDep,
    name: Annotated[str, Form()]
):

    routine = Routine(
        name=name,
        user_id=user.id,
        is_generated=False,
        is_remix=False,
        creation_date=date.today()
    )
    
    try:
        session.add(routine)
    except Exception as e:
        flash(f"An error occurred while saving routine")
        session.rollback()
    session.commit()
    session.refresh(routine)
    flash(request, "Routine created", "success")

    return {"ok": True, "id": routine.id}


@router.post("/routines/{routine_id}/remix")
def remix_routine(routine_id: int, request: Request, user: AuthDep, session: SessionDep):
    original = session.get(Routine, routine_id)
 
    if not original:
        raise HTTPException(status_code=404, detail="Routine not found")
 
    if original.user_id == user.id:
        raise HTTPException(status_code=400, detail="You cannot remix your own routine")
 
    remixed = Routine(
        name=f"{original.name} (Remix)",
        user_id=user.id,
        is_generated=False,
        is_remix=True,
        creation_date=date.today()
    )
    session.add(remixed)
    session.flush()  # get remixed.id before commit
 
    original_links = session.exec(
        select(RoutineWorkout).where(RoutineWorkout.routine_id == routine_id)
    ).all()
 
    for link in original_links:
        new_link = RoutineWorkout(
            routine_id=remixed.id,
            workout_id=link.workout_id,
            difficulty=link.difficulty,
            order_in_routine=link.order_in_routine,
            sets=link.sets,
            reps=link.reps,
            duration_seconds=link.duration_seconds,
            is_warmup=link.is_warmup,
            is_cooldown=link.is_cooldown,
        )
        session.add(new_link)
 
    session.commit()
    session.refresh(remixed)
    flash(request, f'"{original.name}" remixed successfully!', "success")
 
    return {"ok": True, "id": remixed.id}

# =========================
# GET SINGLE ROUTINE (FOR MODAL)
# =========================
@router.get("/routines/{routine_id}")
def get_routine(routine_id: int, user: AuthDep, session: SessionDep):

    routine = session.get(Routine, routine_id)

    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    if routine.user_id != user.id and not routine.is_generated:
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

@router.delete("/routines/{routine_id}")
def delete_routine(routine_id: int, user: AuthDep, session: SessionDep):
    routine = session.get(Routine, routine_id)

    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    if routine.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    workouts = routine.workouts
    for w in workouts:
        session.delete(w)
    session.delete(routine)
    session.commit()

    return {"ok": True}


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