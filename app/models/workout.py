from sqlmodel import Field, SQLModel, Relationship
from typing import Optional

class MuscleGroup(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key = True)
    name: str

    workouts: list['Workout'] = Relationship(back_populates = "muscle_grp")

class WorkoutBase(SQLModel):
    name: str
    video_url: str
    difficulty: str
    workout_type: str
    equipment: Optional[str] = None
    created_by: Optional[int] = Field(default = None, foreign_key = "user.id")
    # is_public: bool = True
    # low, medium, high
    intensity: str

class Workout(WorkoutBase, table = True):
    id: Optional[int] = Field(default=None, primary_key = True)
    muscle_group_id: int = Field(foreign_key = "musclegroup.id")

    muscle_grp: MuscleGroup = Relationship(back_populates = "workouts")
    logs: list['WorkoutLog'] = Relationship(back_populates = "workout")
    routines: list['RoutineWorkout'] = Relationship(back_populates="workout")