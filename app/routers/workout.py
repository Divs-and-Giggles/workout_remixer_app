from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form, APIRouter
from app.dependencies import SessionDep, AuthDep
from . import router, templates
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from app.config import get_settings
from app.models.workout import *
from sqlmodel import select


@router.get("/workouts", response_class=HTMLResponse)
async def workout_view(request:Request, user:AuthDep, db:SessionDep):
      workouts = db.exec(select(Workout)).all()
      return templates.TemplateResponse(
          request=request, 
          name="workout.html",
          context={"user":user,
                   "workouts":workouts
                   }
    )
@router.get("/workouts/{query}", response_class=HTMLResponse)
async def workout_view(request:Request, user:AuthDep, db:SessionDep, query: str):
      workouts = db.exec(select(Workout)).all()
      query_workout= db.exec(select(Workout).where(Workout.name == query, Workout.workout_type == query)).all()
      selected_workout= db.exec(select(Workout).where(Workout.id == query)).all()
      return templates.TemplateResponse(
          request=request, 
          name="workout.html",
          context={"user":user,
                   "query_workout":query_workout,
                   "selected_workout":selected_workout
                   }
    )
