import typer
from app.database import create_db_and_tables, get_cli_session, drop_all
from app.models.user import *
from app.models.workout import Workout, MuscleGroup
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from app.utilities.security import encrypt_password

cli = typer.Typer()

@cli.command()
def initialize():
    with get_cli_session() as db:
        drop_all() 
        create_db_and_tables() 
        
        bob = UserBase(username='bob', email='bob@mail.com', password=encrypt_password("bobpass"))
        bob_db = User.model_validate(bob)
        db.add(bob_db)
        db.commit()


        workout_data = [
            # Warmups and cooldowns
            {"name": "Jumping Jacks", "video_url": "https://www.youtube.com/watch?v=c4DAnQ6DtF8", "difficulty": "easy", "workout_type": "warmup", "equipment": "none", "intensity": "low", "muscle": "Full"},
            {"name": "Arm Circles", "video_url": "https://www.youtube.com/watch?v=1gQy8a9j2sM", "difficulty": "easy", "workout_type": "warmup", "equipment": "none", "intensity": "low", "muscle": "Shoulders"},
            {"name": "High Knees", "video_url": "https://www.youtube.com/watch?v=OAJ_J3EZkdY", "difficulty": "medium", "workout_type": "warmup", "equipment": "none", "intensity": "medium", "muscle": "Legs"},
            {"name": "Hamstring Stretch", "video_url": "https://www.youtube.com/watch?v=Z2n58m2i4jg", "difficulty": "easy", "workout_type": "cooldown", "equipment": "none", "intensity": "low", "muscle": "Legs"},
            {"name": "Quad Stretch", "video_url":"https://www.youtube.com/watch?v=5XHjD8rQ0nE", "difficulty":"easy", "workout_type":"cooldown", "equipment":"none", "intensity":"low", "muscle": "Legs"},
            {"name": "Child's Pose", "video_url":"https://www.youtube.com/watch?v=ZToicYcHIOU", "difficulty":"easy", "workout_type":"cooldown", "equipment":"none", "intensity":"low", "muscle": "Full"},

            # Chest
            {"name": "Push-ups", "video_url": "https://www.youtube.com/watch?v=_l3ySVKYVJ8", "difficulty": "medium", "workout_type": "strength", "equipment": "none", "intensity": "medium", "muscle": "Chest"},
            {"name": "Chest Press with Dumbbells", "video_url": "https://www.youtube.com/watch?v=VmB1G1K7v94", "difficulty": "medium", "workout_type": "strength", "equipment": "dumbbells", "intensity": "medium", "muscle": "Chest"},
            {"name": "Incline Push-ups", "video_url": "https://www.youtube.com/watch?v=8wHjXyYqjWE", "difficulty":"easy", "workout_type":"strength", "equipment":"none", "intensity":"low", "muscle": "Chest"},
            {"name": "Decline Push-ups", "video_url": "https://www.youtube.com/watch?v=0pkjOk0EiAk", "difficulty":"hard", "workout_type":"strength", "equipment":"none", "intensity":"high", "muscle": "Chest"},
            {"name": "Chest Fly with Dumbbells", "video_url":"https://www.youtube.com/watch?v=eozdVDA78K0", "difficulty":"medium", "workout_type":"strength", "equipment":"dumbbells", "intensity":"medium", "muscle": "Chest"},
            {"name": "Cable Crossover", "video_url":"https://www.youtube.com/watch?v=taI4XduLpTk", "difficulty":"medium", "workout_type":"strength", "equipment":"cable machine", "intensity":"medium", "muscle": "Chest"},
            {"name": "Explosive Push-ups", "video_url":"https://www.youtube.com/watch?v=V8QbG9X9JkI", "difficulty":"hard", "workout_type":"strength", "equipment":"none", "intensity":"high", "muscle": "Chest"},
            {"name": "Bench Press", "video_url":"https://www.youtube.com/watch?v=gRVjAtPip0Y", "difficulty":"medium", "workout_type":"strength", "equipment":"barbell", "intensity":"medium", "muscle": "Chest"},
            {"name": "Weighted Dips", "video_url":"https://www.youtube.com/watch?v=6kALZikXxLc", "difficulty":"hard", "workout_type":"strength", "equipment":"dip belt", "intensity":"high", "muscle": "Chest"},

            # Back
            {"name": "Pull-ups", "video_url": "https://www.youtube.com/watch?v=eGo4IYlbE5g", "difficulty": "hard", "workout_type": "strength", "equipment": "pull-up bar", "intensity": "high", "muscle": "Back"},
            {"name": "Bent-over Rows with Dumbbells", "video_url": "https://www.youtube.com/watch?v=6TSP1TRMUzs", "difficulty": "medium", "workout_type": "strength", "equipment": "dumbbells", "intensity": "medium", "muscle": "Back"},
            {"name": "Lat Pulldown", "video_url": "https://www.youtube.com/watch?v=CAwf7n6Luuc", "difficulty":"medium", "workout_type":"strength", "equipment":"lat pulldown machine", "intensity":"medium", "muscle": "Back"},
            {"name": "Deadlifts", "video_url": "https://www.youtube.com/watch?v=op9kVnSso6Q", "difficulty": "hard", "workout_type": "strength", "equipment": "barbell", "intensity": "high", "muscle": "Back"},
            {"name": "Weighted Pull-ups", "video_url": "https://www.youtube.com/watch?v=JZQA08SlJnM", "difficulty": "hard", "workout_type": "strength", "equipment": "pull-up bar and weight belt", "intensity": "high", "muscle": "Back"},
            {"name": "Seated Cable Rows", "video_url": "https://www.youtube.com/watch?v=HJSVR_9sC8o", "difficulty": "medium", "workout_type": "strength", "equipment": "cable machine", "intensity": "medium", "muscle": "Back"},
            {"name": "T-Bar Rows", "video_url": "https://www.youtube.com/watch?v=V8QbG9X9JkI", "difficulty": "medium", "workout_type": "strength", "equipment": "t-bar row machine", "intensity": "medium", "muscle": "Back"},
            {"name": "Assisted Pull-ups", "video_url": "https://www.youtube.com/watch?v=HhYl2kFqVqE", "difficulty": "easy", "workout_type": "strength", "equipment": "assisted pull-up machine", "intensity": "low", "muscle": "Back"},
            {"name": "Inverted Rows", "video_url": "https://www.youtube.com/watch?v=8TtW9bqQYpI", "difficulty": "medium", "workout_type": "strength", "equipment": "suspension trainer or bar", "intensity": "medium", "muscle": "Back"},

            # Legs
            {"name": "Squats", "video_url": "https://www.youtube.com/watch?v=aclHkVaku9U", "difficulty": "medium", "workout_type": "strength", "equipment": "none", "intensity": "medium", "muscle": "Legs"},
            {"name": "Lunges", "video_url": "https://www.youtube.com/watch?v=QOVaHwm-Q6U", "difficulty": "medium", "workout_type": "strength", "equipment": "none", "intensity": "medium", "muscle": "Legs"},
            {"name": "Leg Press", "video_url": "https://www.youtube.com/watch?v=IZxyjW7MPJQ", "difficulty":"medium", "workout_type":"strength", "equipment":"leg press machine", "intensity":"medium", "muscle": "Legs"},
            {"name": "Bulgarian Split Squats", "video_url": "https://www.youtube.com/watch?v=2C-uNgKwPLE", "difficulty": "medium", "workout_type": "strength", "equipment": "none or dumbbells for added resistance", "intensity": "medium", "muscle": "Legs"},
            {"name": "Calf Raises", "video_url":"https://www.youtube.com/watch?v=-M4-G8p8fmc", "difficulty":"easy", "workout_type":"strength", "equipment":"none or calf raise machine for added resistance", 	"intensity":"low", "muscle": "Legs"},
            {"name":"Glute Bridges","video_url":"https://www.youtube.com/watch?v=m2Zx-5yVYFQ","difficulty":"easy","workout_type":"strength","equipment":"none or barbell for added resistance","intensity":"low", "muscle": "Legs"},
            {"name": "Barbell Squats", "video_url": "https://www.youtube.com/watch?v=Dy28eq2PjcM", "difficulty": "hard", "workout_type": "strength", "equipment": "barbell", "intensity": "high", "muscle": "Legs"},
            {"name": "Romanian Deadlifts", "video_url": "https://www.youtube.com/watch?v=2SHsk9AzdjA", "difficulty": "medium", "workout_type": "strength", "equipment": "barbell or dumbbells", "intensity": "medium", "muscle": "Legs"},
            {"name": "Leg Extensions", "video_url": "https://www.youtube.com/watch?v=YyvSfVjQeL0", "difficulty": "medium", "workout_type": "strength", "equipment": "leg extension machine", "intensity": "medium", "muscle": "Legs"},

            # Shoulders
            {"name": "Overhead Press with Dumbbells", "video_url": "https://www.youtube.com/watch?v=B-aVuyhvLHU", "difficulty": "medium", "workout_type": "strength", "equipment": "dumbbells", "intensity": "medium", "muscle": "Shoulders"},
            {"name": "Lateral Raises with Dumbbells", "video_url": "https://www.youtube.com/watch?v=3VcKaXpzqRo", "difficulty": "medium", "workout_type": "strength", "equipment": "dumbbells", "intensity": "medium", "muscle": "Shoulders"},
            {"name": "Front Raises with Dumbbells", "video_url": "https://www.youtube.com/watch?v=-t7fuZ0KhDA", "difficulty": "medium", "workout_type": "strength", "equipment": "dumbbells", "intensity": "medium", "muscle": "Shoulders"},
            {"name": "Arnold Press with Dumbbells", "video_url":"https://www.youtube.com/watch?v=vj2w851ZHRM","difficulty":"medium","workout_type":"strength","equipment":"dumbbells","intensity":"medium", "muscle": "Shoulders"},
            {"name":"Reverse Fly with Dumbbells","video_url":"https://www.youtube.com/watch?v=6kALZikXxLc","difficulty":"medium","workout_type":"strength","equipment":"dumbbells","intensity":"medium", "muscle": "Shoulders"},
            {"name": "Pike Push-ups", "video_url": "https://www.youtube.com/watch?v=CNpXHqz9qj8", "difficulty": "medium", "workout_type": "strength", "equipment": "none", "intensity": "medium", "muscle": "Shoulders"},
            {"name": "Handstand Push-ups", "video_url": "https://www.youtube.com/watch?v=0AUGkch3tzc", "difficulty": "hard", "workout_type": "strength", "equipment": "none", "intensity": "high", "muscle": "Shoulders"},
            {"name": "Advanced Pike Push-ups", "video_url": "https://www.youtube.com/watch?v=2z8JmcrW-As", "difficulty": "hard", "workout_type": "strength", "equipment": "none", "intensity": "high", "muscle": "Shoulders"},
            {"name": "Planche Leans", "video_url": "https://www.youtube.com/watch?v=9QxHj8rjSg8", "difficulty": "hard", "workout_type": "strength", "equipment": "none", "intensity": "high", "muscle": "Shoulders"},

            # Arms
            {"name": "Bicep Curls with Dumbbells", "video_url": "https://www.youtube.com/watch?v=ykJmrZ5v0Oo", "difficulty": "medium", "workout_type": "strength", "equipment": "dumbbells", "intensity": "medium", "muscle": "Arms"},
            {"name": "Tricep Dips", "video_url": "https://www.youtube.com/watch?v=0326dy_-CzM", "difficulty": "medium", "workout_type": "strength", "equipment": "parallel bars or bench", "intensity": "medium", "muscle": "Arms"},
            {"name": "Hammer Curls with Dumbbells", "video_url": "https://www.youtube.com/watch?v=zC3nLlEvin4", "difficulty": "medium", "workout_type": "strength", "equipment": "dumbbells", "intensity": "medium", "muscle": "Arms"},
            {"name": "Overhead Tricep Extension with Dumbbell", "video_url": "https://www.youtube.com/watch?v=_gsUck-7M74", "difficulty": "medium", "workout_type": "strength", "equipment": "dumbbell", "intensity": "medium", "muscle": "Arms"},
            {"name": "Concentration Curls with Dumbbells", "video_url": "https://www.youtube.com/watch?v=soxrZlIl35w", "difficulty": "medium", "workout_type": "strength", "equipment": "dumbbells", "intensity": "medium", "muscle": "Arms"},
            {"name": "Close-grip Push-ups", "video_url":"https://www.youtube.com/watch?v=0AUGkch3tzc","difficulty":"medium","workout_type":"strength","equipment":"none","intensity":"medium", "muscle": "Arms"},
            {"name":"Diamond Push-ups","video_url":"https://www.youtube.com/watch?v=J0DnG1_S92I","difficulty":"hard","workout_type":"strength","equipment":"none","intensity":"high", "muscle": "Arms"},
            {"name":"Zottman Curls with Dumbbells","video_url":"https://www.youtube.com/watch?v=twD-YGVP4Bk","difficulty":"medium","workout_type":"strength","equipment":"dumbbells","intensity":"medium", "muscle": "Arms"},
            {"name":"Skull Crushers with Dumbbells","video_url":"https://www.youtube.com/watch?v=d_KZxkY_0cM","difficulty":"medium","workout_type":"strength","equipment":"dumbbells","intensity":"medium", "muscle": "Arms"},

            # Core
            {"name": "Plank", "video_url": "https://www.youtube.com/watch?v=801294732", "difficulty": "medium", "workout_type": "strength", "equipment": "none", "intensity": "medium", "muscle": "Core"},
            {"name": "Russian Twists", "video_url": "https://www.youtube.com/watch?v=801294732", "difficulty": "medium", "workout_type": "strength", "equipment": "none", "intensity": "medium", "muscle": "Core"},
            {"name": "Leg Raises", "video_url": "https://www.youtube.com/watch?v=JB2oyawG9KI", "difficulty": "medium", "workout_type": "strength", "equipment": "none", "intensity": "medium", "muscle": "Core"},
            {"name": "Bicycle Crunches", "video_url": "https://www.youtube.com/watch?v=9FGilxCbdz8", "difficulty": "medium", "workout_type": "strength", "equipment": "none", "intensity": "medium", "muscle": "Core"},
            {"name": "Mountain Climbers", "video_url": "https://www.youtube.com/watch?v=nmwgirgXLYM", "difficulty": "medium", "workout_type": "strength", "equipment": "none", "intensity": "medium", "muscle": "Core"},
            {"name": "Hanging Leg Raises", "video_url": "https://www.youtube.com/watch?v=JB2oyawG9KI", "difficulty": "hard", "workout_type": "strength", "equipment": "pull-up bar", "intensity": "high", "muscle": "Core"},
            {"name": "V-Ups", "video_url": "https://www.youtube.com/watch?v=JB2oyawG9KI", "difficulty": "hard", "workout_type": "strength", "equipment": "none", "intensity": "high", "muscle": "Core"},
            {"name": "Dragon Flags", "video_url": "https://www.youtube.com/watch?v=6TSP1TRMUzs", "difficulty": "hard", "workout_type": "strength", "equipment": "none", "intensity": "high", "muscle": "Core"},
            {"name": "Ab Wheel Rollouts", "video_url": "https://www.youtube.com/watch?v=H0V7QyTqShs", "difficulty": "hard", "workout_type": "strength", "equipment": "ab wheel", "intensity": "high", "muscle": "Core"}
        ]

        muscle_names = ["chest", "back", "legs", "shoulders", "arms", "core", "full"]
        for name in muscle_names:
            muscle = MuscleGroup(name=name)
            db.add(muscle)
        db.commit()

        def get_muscle_id(muscle_name):
            muscle_grps = db.exec(select(MuscleGroup)).all()

            for muscle in muscle_grps:
                if muscle.name.lower() == muscle_name.lower():
                    return muscle.id
            return None
        
        for workout in workout_data:
            muscle_id = get_muscle_id(workout["muscle"])

            workout_db = Workout(
                name=workout["name"],
                video_url=workout["video_url"],
                difficulty=workout["difficulty"],
                workout_type=workout["workout_type"],
                equipment=workout["equipment"],
                intensity=workout["intensity"],
                created_by=bob_db.id,
                muscle_group_id=muscle_id
            )
            db.add(workout_db)
        db.commit()

        print("Database Initialized")

@cli.command()
def test():
    print("You're already in the test")


if __name__ == "__main__":
    cli()