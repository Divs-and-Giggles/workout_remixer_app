from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from app.models import *

class MuscleGroup(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key = True)
    name: str

    workouts: list['WorkoutMuscle'] = Relationship(back_populates = "muscle_group")

class Workout(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key = True)
    name: str
    video_url: Optional[str]= None
    difficulty: str
    workout_type: str
    equipment: Optional[str] = None
    created_by: Optional[int] = Field(default = None, foreign_key = "user.id")
    is_public: bool = True
    intensity: float
    instructions: Optional[str] = None

    muscles: list['WorkoutMuscle'] = Relationship(back_populates = "workout")
    logs: list['WorkoutLog'] = Relationship(back_populates = "workout")
