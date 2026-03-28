from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import date

class Routine(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    difficulty: str
    user_id: int = Field(default=None, foreign_key="user.id")
    is_generated: bool = False
    creation_date: date
    times_used: int = 0
    last_used: Optional[date] = None

    user: Optional["User"] = Relationship(back_populates="routines")
    workouts: list['RoutineWorkout'] = Relationship(back_populates="routine")
    sessions: list['WorkoutSession'] = Relationship(back_populates="routine")

class RoutineWorkout(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    routine_id: int = Field(default = None, foreign_key="routine.id")
    workout_id: int = Field(default=None, foreign_key="workout.id")
    order_in_routine: int
    sets: int
    reps: int
    is_warmup: bool = False
    is_cooldown: bool = False

    routine: Optional["Routine"] = Relationship(back_populates="workouts")