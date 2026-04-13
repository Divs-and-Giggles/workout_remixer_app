from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date

from app.models.user import User
from app.models.workout import Workout
from app.models.logging import WorkoutSession


class Routine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    difficulty: str = "beginner"

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    is_generated: bool = False
    creation_date: date

    times_used: int = 0
    last_used: Optional[date] = None

    user: Optional["User"] = Relationship(back_populates="routines")
    workouts: List["RoutineWorkout"] = Relationship(back_populates="routine")
    sessions: List["WorkoutSession"] = Relationship(back_populates="routine")

class RoutineWorkout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    routine_id: int = Field(foreign_key="routine.id")
    workout_id: int = Field(foreign_key="workout.id")

    difficulty: str
    order_in_routine: int

    sets: int
    reps: Optional[int] = None
    duration_seconds: Optional[int] = None

    is_warmup: bool = False
    is_cooldown: bool = False

    workout: Optional["Workout"] = Relationship(back_populates="routines")
    routine: Optional["Routine"] = Relationship(back_populates="workouts")

# CREATE ROUTINE (POST)
class RoutineCreate(SQLModel):
    name: str
    difficulty: str = "beginner"
    is_generated: bool = False


# UPDATE ROUTINE (PUT) 
class RoutineUpdate(SQLModel):
    name: Optional[str] = None
    difficulty: Optional[str] = None
    is_generated: Optional[bool] = None


# READ ROUTINE (FOR FRONTEND DISPLAY)
class RoutineRead(SQLModel):
    id: int
    name: str
    difficulty: str
    user_id: int
    is_generated: bool
    creation_date: date
    times_used: int
    last_used: Optional[date]
    
# REMIX 
class RoutineRemix(SQLModel):
    name: Optional[str] = None