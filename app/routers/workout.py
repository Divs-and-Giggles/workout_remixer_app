from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form, APIRouter, HTTPException, Depends, Request, Response, Form,  Query
from app.dependencies import SessionDep, AuthDep
from . import router, templates
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from app.config import get_settings
from app.models.workout import *
from sqlmodel import select,func
from app.pagination import Pagination
from app.models.routine import Routine


@router.get("/workouts", response_class=HTMLResponse)
async def workout_view(request:Request, user:AuthDep, db:SessionDep, page: int = Query(default=1, ge=1), limit: int = Query(default=12, le=100), q: str = Query(default=''), done: str = Query(default='')):
    offset = (page-1)*limit
    query =  select(Workout).join(MuscleGroup, Workout.muscle_group_id == MuscleGroup.id)
    if q:
        query = query.where(
            Workout.name.ilike(f"%{q}%") |
            Workout.workout_type.ilike(f"%{q}%") |
            Workout.equipment.ilike(f"%{q}%")
        )

    # Dropdown filter — only one active at a time
    if done:
        equipment_filters = {
            "body weight": Workout.equipment.ilike(f"%body weight%"),
            "barbell":     Workout.equipment.ilike(f"%barbell%"),
            "dumbbell":    Workout.equipment.ilike(f"%dumbbell%"),
            "machine":     Workout.equipment.ilike(f"%machine%"),
            "bar":         Workout.equipment.ilike(f"%bar%"),
        }
        muscle_filters = {"arms", "chest", "back", "legs", "shoulders", "core", "full"}
        difficulty_filters = {"easy", "medium", "hard"}

        if done in equipment_filters:
            query = query.where(equipment_filters[done])
        elif done in muscle_filters:
            query = query.where(MuscleGroup.name == done)
        elif done in difficulty_filters:
            query = query.where(Workout.difficulty == done)

    # Count filtered results for correct pagination
    count_workouts = db.exec(select(func.count()).select_from(query.subquery())).one()

    # Apply pagination to the same filtered query
    workouts = db.exec(query.offset(offset).limit(limit)).all()
    routines= db.exec(select(Routine).where(Routine.user_id == user.id)).all()

    pagination = Pagination(total_count=count_workouts, current_page=page, limit=limit)
    return templates.TemplateResponse(
        request=request,
        name="workout.html",
        context={
            "user": user,
            "workouts": workouts,
            "pagination": pagination,
            "routines": routines,
            "q": q,
            "done": done
        }
    )
        
    
