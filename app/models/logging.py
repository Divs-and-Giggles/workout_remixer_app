from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import date

class WorkoutSession(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id") 
    routine_id: int = Field(default=None, foreign_key="routine.id")
    workout_date: date
    duration: Optional[int]

    user: Optional["User"] = Relationship(back_populates="sessions")
    routine: Optional["Routine"] = Relationship(back_populates="sessions")
    logs: list['WorkoutLog'] = Relationship(back_populates="session")

class WorkoutLog(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(default= None, foreign_key="workoutsession.id")
    workout_id: int = Field(default=None, foreign_key="workout.id")
    sets: int 
    reps: int
    weight: Optional[float] = None
    completed: bool = False
    difficulty: Optional[str] = None
    date: date
    session: Optional["WorkoutSession"] = Relationship(back_populates="logs")
    workout: Optional["Workout"] = Relationship(back_populates="logs")

class DailySteps(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    steps:int
    date:date

class WaterIntake(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    amount_ml: int
    date: date