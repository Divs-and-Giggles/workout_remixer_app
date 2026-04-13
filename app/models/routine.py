from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date

from app.models.user import User
from app.models.workout import Workout
from app.models.logging import WorkoutSession


# =========================
# ROUTINE TABLE
# =========================
class Routine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str
    difficulty: str = "beginner"

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    is_system: bool = Field(default=False, nullable=False)
    is_remix: bool = Field(default=False, nullable=False)

    creation_date: date = Field(default_factory=date.today)

    times_used: int = 0
    last_used: Optional[date] = None

    user: Optional["User"] = Relationship(back_populates="routines")
    workouts: List["RoutineWorkout"] = Relationship(back_populates="routine")
    sessions: list["WorkoutSession"] = Relationship(back_populates="routine")

# =========================
# ROUTINE ↔ WORKOUT LINK TABLE
# =========================
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


# =========================
# CREATE SCHEMA
# =========================
class RoutineCreate(SQLModel):
    name: str
    difficulty: str = "beginner"
    is_generated: bool = False


# =========================
# UPDATE SCHEMA
# =========================
class RoutineUpdate(SQLModel):
    name: Optional[str] = None
    difficulty: Optional[str] = None
