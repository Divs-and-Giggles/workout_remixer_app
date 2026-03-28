from sqlmodel import Field, SQLModel, Relationship
from typing import Optional

class WorkoutMuscle(SQLModel, table = True):
    muscle_group_id: int = Field(default=None, foreign_key="musclegroup.id", primary_key= True)
    workout_id: int = Field(default=None, foreign_key="workout.id", primary_key=True)

    workout: Optional["Workout"] = Relationship(back_populates="muscles")
    muscle_group: Optional["MuscleGroup"] = Relationship(back_populates="workouts")

class WorkoutAlternative(SQLModel, table = True):
    workout_id: int = Field(default = None, foreign_key="workout.id", primary_key=True)
    alt_workout_id: int = Field(default=None, foreign_key="workout.id", primary_key=True)