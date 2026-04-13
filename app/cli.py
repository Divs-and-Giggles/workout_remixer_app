import csv
from pathlib import Path

import typer
from app.database import create_db_and_tables, get_cli_session, drop_all
from app.models.other import WorkoutGif
from app.models.routine import Routine, RoutineWorkout
from app.models.workout import Workout, MuscleGroup
from app.models.user import *
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from app.utilities.security import encrypt_password
from datetime import date

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
            # Warmups
            {"name": "Jumping Jacks", "video_url": "https://www.youtube.com/watch?v=c4DAnQ6DtF8", "difficulty": "easy", "workout_type": "warmup", "equipment": "body", "intensity": "low", "muscle": "Full"},
            {"name": "Arm Circles", "video_url": "https://www.youtube.com/watch?v=1gQy8a9j2sM", "difficulty": "easy", "workout_type": "warmup", "equipment": "body", "intensity": "low", "muscle": "Shoulders"},
            {"name": "High Knees", "video_url": "https://www.youtube.com/watch?v=OAJ_J3EZkdY", "difficulty": "medium", "workout_type": "warmup", "equipment": "body", "intensity": "medium", "muscle": "Legs"},
            {"name": "Wrist Circles", "video_url": "https://www.youtube.com/watch?v=1gQy8a9j2sM", "difficulty": "easy", "workout_type": "warmup", "equipment": "body", "intensity": "low", "muscle": "Arms"},
            {"name": "Shoulder Rolls", "video_url": "https://www.youtube.com/watch?v=1gQy8a9j2sM", "difficulty": "easy", "workout_type": "warmup", "equipment": "body", "intensity": "low", "muscle": "Shoulders"},
            {"name": "Jog in Place", "video_url": "https://www.youtube.com/watch?v=OAJ_J3EZkdY", "difficulty": "easy", "workout_type": "warmup", "equipment": "body", "intensity": "low", "muscle": "Full"},
            {"name": "Hip Flexor Stretch", "video_url": "https://www.youtube.com/watch?v=Z2n58m2i4jg", "difficulty": "easy", "workout_type": "warmup", "equipment": "body", "intensity": "low", "muscle": "Legs"},

            # Cooldowns
            {"name": "Hamstring Stretch", "video_url": "https://www.youtube.com/watch?v=Z2n58m2i4jg", "difficulty": "easy", "workout_type": "cooldown", "equipment": "body", "intensity": "low", "muscle": "Legs"},
            {"name": "Quad Stretch", "video_url":"https://www.youtube.com/watch?v=5XHjD8rQ0nE", "difficulty":"easy", "workout_type":"cooldown", "equipment":"body", "intensity":"low", "muscle": "Legs"},
            {"name": "Child's Pose", "video_url":"https://www.youtube.com/watch?v=ZToicYcHIOU", "difficulty":"easy", "workout_type":"cooldown", "equipment":"body", "intensity":"low", "muscle": "Full"},
            {"name": "Shoulder Stretch", "video_url":"https://www.youtube.com/watch?v=ZToicYcHIOU", "difficulty":"easy", "workout_type":"cooldown", "equipment":"body", "intensity":"low", "muscle": "Shoulders"},
            {"name": "Tricep Stretch", "video_url":"https://www.youtube.com/watch?v=ZToicYcHIOU", "difficulty":"easy", "workout_type":"cooldown", "equipment":"body", "intensity":"low", "muscle": "Arms"},
            {"name": "Chest Stretch", "video_url":"https://www.youtube.com/watch?v=ZToicYcHIOU", "difficulty":"easy", "workout_type":"cooldown", "equipment":"body", "intensity":"low", "muscle": "Chest"},
            {"name": "Cat-Cow Stretch", "video_url":"https://www.youtube.com/watch?v=kqnua4rHVVA", "difficulty":"easy", "workout_type":"cooldown", "equipment":"body", "intensity":"low", "muscle": "Back"},
            {"name": "Seated Forward Bend", "video_url":"https://www.youtube.com/watch?v=4pKly2JojMw", "difficulty":"easy", "workout_type":"cooldown", "equipment":"body", "intensity":"low", "muscle": "Back"},
            {"name": "Bicep Stretch", "video_url":"https://www.youtube.com/watch?v=ZToicYcHIOU", "difficulty":"easy", "workout_type":"cooldown", "equipment":"body", "intensity":"low", "muscle": "Arms"},

            # Chest
            {"name": "Push-ups", "video_url": "https://www.youtube.com/watch?v=_l3ySVKYVJ8", "difficulty": "medium", "workout_type": "endurance", "equipment": "body", "intensity": "medium", "muscle": "Chest"},
            {"name": "Chest Press with Dumbbells", "video_url": "https://www.youtube.com/watch?v=VmB1G1K7v94", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "dumbbells", "intensity": "medium", "muscle": "Chest"},
            {"name": "Incline Push-ups", "video_url": "https://www.youtube.com/watch?v=8wHjXyYqjWE", "difficulty":"easy", "workout_type":"endurance", "equipment":"body", "intensity":"low", "muscle": "Chest"},
            {"name": "Decline Push-ups", "video_url": "https://www.youtube.com/watch?v=0pkjOk0EiAk", "difficulty":"hard", "workout_type":"endurance", "equipment":"body", "intensity":"high", "muscle": "Chest"},
            {"name": "Chest Fly with Dumbbells", "video_url":"https://www.youtube.com/watch?v=eozdVDA78K0", "difficulty":"medium", "workout_type":"hypertrophy", "equipment":"dumbbells", "intensity":"medium", "muscle": "Chest"},
            {"name": "Cable Crossover", "video_url":"https://www.youtube.com/watch?v=taI4XduLpTk", "difficulty":"medium", "workout_type":"hypertrophy", "equipment":"cable machine", "intensity":"medium", "muscle": "Chest"},
            {"name": "Explosive Push-ups", "video_url":"https://www.youtube.com/watch?v=V8QbG9X9JkI", "difficulty":"hard", "workout_type":"strength", "equipment":"body", "intensity":"high", "muscle": "Chest"},
            {"name": "Bench Press", "video_url":"https://www.youtube.com/watch?v=gRVjAtPip0Y", "difficulty":"medium", "workout_type":"strength", "equipment":"barbell", "intensity":"medium", "muscle": "Chest"},
            {"name": "Weighted Dips", "video_url":"https://www.youtube.com/watch?v=6kALZikXxLc", "difficulty":"hard", "workout_type":"strength", "equipment":"dip belt", "intensity":"high", "muscle": "Chest"},

            # Back
            {"name": "Pull-ups", "video_url": "https://www.youtube.com/watch?v=eGo4IYlbE5g", "difficulty": "hard", "workout_type": "strength", "equipment": "pull-up bar", "intensity": "high", "muscle": "Back"},
            {"name": "Bent-over Rows with Dumbbells", "video_url": "https://www.youtube.com/watch?v=6TSP1TRMUzs", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "dumbbells", "intensity": "medium", "muscle": "Back"},
            {"name": "Lat Pulldown", "video_url": "https://www.youtube.com/watch?v=CAwf7n6Luuc", "difficulty":"medium", "workout_type":"hypertrophy", "equipment":"lat pulldown machine", "intensity":"medium", "muscle": "Back"},
            {"name": "Deadlifts", "video_url": "https://www.youtube.com/watch?v=op9kVnSso6Q", "difficulty": "hard", "workout_type": "strength", "equipment": "barbell", "intensity": "high", "muscle": "Back"},
            {"name": "Weighted Pull-ups", "video_url": "https://www.youtube.com/watch?v=JZQA08SlJnM", "difficulty": "hard", "workout_type": "strength", "equipment": "pull-up bar and weight belt", "intensity": "high", "muscle": "Back"},
            {"name": "Seated Cable Rows", "video_url": "https://www.youtube.com/watch?v=HJSVR_9sC8o", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "cable machine", "intensity": "medium", "muscle": "Back"},
            {"name": "T-Bar Rows", "video_url": "https://www.youtube.com/watch?v=V8QbG9X9JkI", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "t-bar row machine", "intensity": "medium", "muscle": "Back"},
            {"name": "Assisted Pull-ups", "video_url": "https://www.youtube.com/watch?v=HhYl2kFqVqE", "difficulty": "easy", "workout_type": "endurance", "equipment": "assisted pull-up machine", "intensity": "low", "muscle": "Back"},
            {"name": "Inverted Rows", "video_url": "https://www.youtube.com/watch?v=8TtW9bqQYpI", "difficulty": "medium", "workout_type": "endurance", "equipment": "suspension trainer or bar", "intensity": "medium", "muscle": "Back"},

            # Legs
            {"name": "Squats", "video_url": "https://www.youtube.com/watch?v=aclHkVaku9U", "difficulty": "medium", "workout_type": "strength", "equipment": "body", "intensity": "medium", "muscle": "Legs"},
            {"name": "Lunges", "video_url": "https://www.youtube.com/watch?v=QOVaHwm-Q6U", "difficulty": "medium", "workout_type": "endurance", "equipment": "body", "intensity": "medium", "muscle": "Legs"},
            {"name": "Leg Press", "video_url": "https://www.youtube.com/watch?v=IZxyjW7MPJQ", "difficulty":"medium", "workout_type":"strength", "equipment":"leg press machine", "intensity":"medium", "muscle": "Legs"},
            {"name": "Bulgarian Split Squats", "video_url": "https://www.youtube.com/watch?v=2C-uNgKwPLE", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "body or dumbbells for added resistance", "intensity": "medium", "muscle": "Legs"},
            {"name": "Calf Raises", "video_url":"https://www.youtube.com/watch?v=-M4-G8p8fmc", "difficulty":"easy", "workout_type":"hypertrophy", "equipment":"body or calf raise machine for added resistance", 	"intensity":"low", "muscle": "Legs"},
            {"name":"Glute Bridges","video_url":"https://www.youtube.com/watch?v=m2Zx-5yVYFQ","difficulty":"easy","workout_type":"hypertrophy","equipment":"body or barbell for added resistance","intensity":"low", "muscle": "Legs"},
            {"name": "Barbell Squats", "video_url": "https://www.youtube.com/watch?v=Dy28eq2PjcM", "difficulty": "hard", "workout_type": "strength", "equipment": "barbell", "intensity": "high", "muscle": "Legs"},
            {"name": "Romanian Deadlifts", "video_url": "https://www.youtube.com/watch?v=2SHsk9AzdjA", "difficulty": "medium", "workout_type": "strength", "equipment": "barbell or dumbbells", "intensity": "medium", "muscle": "Legs"},
            {"name": "Leg Extensions", "video_url": "https://www.youtube.com/watch?v=YyvSfVjQeL0", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "leg extension machine", "intensity": "medium", "muscle": "Legs"},

            # Shoulders
            {"name": "Overhead Press with Dumbbells", "video_url": "https://www.youtube.com/watch?v=B-aVuyhvLHU", "difficulty": "medium", "workout_type": "strength", "equipment": "dumbbells", "intensity": "medium", "muscle": "Shoulders"},
            {"name": "Lateral Raises with Dumbbells", "video_url": "https://www.youtube.com/watch?v=3VcKaXpzqRo", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "dumbbells", "intensity": "medium", "muscle": "Shoulders"},
            {"name": "Front Raises with Dumbbells", "video_url": "https://www.youtube.com/watch?v=-t7fuZ0KhDA", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "dumbbells", "intensity": "medium", "muscle": "Shoulders"},
            {"name": "Arnold Press with Dumbbells", "video_url":"https://www.youtube.com/watch?v=vj2w851ZHRM","difficulty":"medium","workout_type":"hypertrophy","equipment":"dumbbells","intensity":"medium", "muscle": "Shoulders"},
            {"name":"Reverse Fly with Dumbbells","video_url":"https://www.youtube.com/watch?v=6kALZikXxLc","difficulty":"medium","workout_type":"hypertrophy","equipment":"dumbbells","intensity":"medium", "muscle": "Shoulders"},
            {"name": "Pike Push-ups", "video_url": "https://www.youtube.com/watch?v=CNpXHqz9qj8", "difficulty": "medium", "workout_type": "endurance", "equipment": "body", "intensity": "medium", "muscle": "Shoulders"},
            {"name": "Handstand Push-ups", "video_url": "https://www.youtube.com/watch?v=0AUGkch3tzc", "difficulty": "hard", "workout_type": "strength", "equipment": "body", "intensity": "high", "muscle": "Shoulders"},
            {"name": "Advanced Pike Push-ups", "video_url": "https://www.youtube.com/watch?v=2z8JmcrW-As", "difficulty": "hard", "workout_type": "strength", "equipment": "body", "intensity": "high", "muscle": "Shoulders"},
            {"name": "Planche Leans", "video_url": "https://www.youtube.com/watch?v=9QxHj8rjSg8", "difficulty": "hard", "workout_type": "strength", "equipment": "body", "intensity": "high", "muscle": "Shoulders"},
            {"name": "Handstand Hold", "video_url": "https://www.youtube.com/watch?v=0AUGkch3tzc", "difficulty": "hard", "workout_type": "endurance", "equipment": "body", "intensity": "high", "muscle": "Shoulders"},
            {"name": "Wall Handstand Push-ups", "video_url": "https://www.youtube.com/watch?v=0AUGkch3tzc", "difficulty": "hard", "workout_type": "strength", "equipment": "body", "intensity": "high", "muscle": "Shoulders"},

            # Arms
            {"name": "Bicep Curls with Dumbbells", "video_url": "https://www.youtube.com/watch?v=ykJmrZ5v0Oo", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "dumbbells", "intensity": "medium", "muscle": "Arms"},
            {"name": "Tricep Dips", "video_url": "https://www.youtube.com/watch?v=0326dy_-CzM", "difficulty": "medium", "workout_type": "strength", "equipment": "parallel bars or bench", "intensity": "medium", "muscle": "Arms"},
            {"name": "Hammer Curls with Dumbbells", "video_url": "https://www.youtube.com/watch?v=zC3nLlEvin4", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "dumbbells", "intensity": "medium", "muscle": "Arms"},
            {"name": "Overhead Tricep Extension with Dumbbell", "video_url": "https://www.youtube.com/watch?v=_gsUck-7M74", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "dumbbell", "intensity": "medium", "muscle": "Arms"},
            {"name": "Concentration Curls with Dumbbells", "video_url": "https://www.youtube.com/watch?v=soxrZlIl35w", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "dumbbells", "intensity": "medium", "muscle": "Arms"},
            {"name": "Tricep Kickbacks with Dumbbells", "video_url": "https://www.youtube.com/watch?v=6SSsL2tWkD8", "difficulty": "medium", "workout_type": "hypertrophy", "equipment": "dumbbells", "intensity": "medium", "muscle": "Arms"},
            {"name":"Diamond Push-ups","video_url":"https://www.youtube.com/watch?v=J0DnG1_S92I","difficulty":"hard","workout_type":"strength","equipment":"body","intensity":"high", "muscle": "Arms"},
            {"name":"Zottman Curls with Dumbbells","video_url":"https://www.youtube.com/watch?v=twD-YGVP4Bk","difficulty":"medium","workout_type":"hypertrophy","equipment":"dumbbells","intensity":"medium", "muscle": "Arms"},
            {"name":"Skull Crushers with Dumbbells","video_url":"https://www.youtube.com/watch?v=d_KZxkY_0cM","difficulty":"medium","workout_type":"hypertrophy","equipment":"dumbbells","intensity":"medium", "muscle": "Arms"},

            # Core
            {"name": "Plank", "video_url": "https://www.youtube.com/watch?v=801294732", "difficulty": "medium", "workout_type": "endurance", "equipment": "body", "intensity": "medium", "muscle": "Core"},
            {"name": "Russian Twists", "video_url": "https://www.youtube.com/watch?v=801294732", "difficulty": "medium", "workout_type": "endurance", "equipment": "body", "intensity": "medium", "muscle": "Core"},
            {"name": "Leg Raises", "video_url": "https://www.youtube.com/watch?v=JB2oyawG9KI", "difficulty": "medium", "workout_type": "endurance", "equipment": "body", "intensity": "medium", "muscle": "Core"},
            {"name": "Bicycle Crunches", "video_url": "https://www.youtube.com/watch?v=9FGilxCbdz8", "difficulty": "medium", "workout_type": "endurance", "equipment": "body", "intensity": "medium", "muscle": "Core"},
            {"name": "Mountain Climbers", "video_url": "https://www.youtube.com/watch?v=nmwgirgXLYM", "difficulty": "medium", "workout_type": "endurance", "equipment": "body", "intensity": "medium", "muscle": "Core"},
            {"name": "Hanging Leg Raises", "video_url": "https://www.youtube.com/watch?v=JB2oyawG9KI", "difficulty": "hard", "workout_type": "strength", "equipment": "pull-up bar", "intensity": "high", "muscle": "Core"},
            {"name": "V-Ups", "video_url": "https://www.youtube.com/watch?v=JB2oyawG9KI", "difficulty": "hard", "workout_type": "endurance", "equipment": "body", "intensity": "high", "muscle": "Core"},
            {"name": "Dragon Flags", "video_url": "https://www.youtube.com/watch?v=6TSP1TRMUzs", "difficulty": "hard", "workout_type": "strength", "equipment": "body", "intensity": "high", "muscle": "Core"},
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

       
        with open('workout_gifs.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                wg= WorkoutGif(
                    workout_id=int(row["workout_id"]),
                    gif_id=str(row["gif_id"]),
                    name=row["workout_name"]
                )
                db.add(wg)
        db.commit()

        routine_data = [
            ### Chest Routines ###
            #Beginner Chest Routine
            {
                "name": "Beginner Chest Routine",
                "difficulty": "beginner",
                "muscle": "Chest",
                "workouts": [
                    # warmups
                    {"name": "Jumping Jacks", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    # main workouts
                    {"name": "Incline Push-ups", "sets":3, "reps": 6},
                    {"name": "Chest Press with Dumbbells", "sets":3, "reps": 6},
                    {"name": "Chest Fly with Dumbbells", "sets":3, "reps": 6},
                    {"name": "Cable Crossover", "sets":3, "reps": 6},
                    # cooldowns
                    {"name": "Shoulder Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True},
                    {"name": "Tricep Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True},
                    {"name": "Chest Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True}
                ]
            },
            # Intermediate Chest Routine
            {
                "name": "Intermediate Chest Routine",
                "difficulty": "intermediate",
                "muscle": "Chest",
                "workouts": [
                    # warmups
                    {"name": "Jumping Jacks", "sets":1, "duration_seconds": 35, "is_warmup": True},
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 35, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 35, "is_warmup": True},
                    # main workouts
                    {"name": "Push-ups", "sets": 3, "reps": 10},
                    {"name": "Chest Press with Dumbbells", "sets": 3, "reps": 10},
                    {"name": "Chest Fly with Dumbbells", "sets": 3, "reps": 10},
                    {"name": "Cable Crossover", "sets": 3, "reps": 10},
                    # cooldowns
                    {"name": "Shoulder Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True},
                    {"name": "Tricep Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True},
                    {"name": "Chest Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True}
                ]
            },
            # Advanced Chest Routine
            {
                "name": "Advanced Chest Routine",
                "difficulty": "advanced",
                "muscle": "Chest",
                "workouts": [
                    # warmups
                    {"name": "Jumping Jacks", "sets":1, "duration_seconds": 40, "is_warmup": True},
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 40, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 40, "is_warmup": True},
                    # main workouts
                    {"name": "Decline Push-ups", "sets": 3, "reps": 15},
                    {"name": "Weighted Dips", "sets": 3, "reps": 15},
                    {"name": "Chest Fly with Dumbbells", "sets": 3, "reps": 15},
                    {"name": "Cable Crossover", "sets": 3, "reps": 15},
                    # cooldowns
                    {"name": "Shoulder Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True},
                    {"name": "Tricep Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True},
                    {"name": "Chest Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True}
                ]
            },
            # Elite Chest Routine
            {
                "name": "Elite Chest Routine",
                "difficulty": "elite",
                "muscle": "Chest",
                "workouts": [
                    # warmups
                    {"name": "Jumping Jacks", "sets":1, "duration_seconds": 45, "is_warmup": True},
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 45, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 45, "is_warmup": True},
                    # main workouts
                    {"name": "Bench Press", "sets": 4, "reps": 25},
                    {"name": "Explosive Push-ups", "sets": 4, "reps": 25},
                    {"name": "Weighted Dips", "sets": 4, "reps": 25},
                    {"name": "Decline Push-ups", "sets": 4, "reps": 25},
                    # cooldowns
                    {"name": "Shoulder Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True},
                    {"name": "Tricep Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True},
                    {"name": "Chest Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True}
                ]
            },
            ### Back Routines ###
            #Beginner Back Routine
            {
                "name": "Beginner Back Routine",
                "difficulty": "beginner",
                "muscle": "Back",
                "workouts": [
                    # warmups
                    {"name": "Jumping Jacks", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    # main workouts
                    {"name": "Assisted Pull-ups", "sets":3, "reps": 6},
                    {"name": "Seated Cable Rows", "sets":3, "reps": 6},
                    {"name": "T-Bar Rows", "sets":3, "reps": 6},
                    {"name": "Inverted Rows", "sets":3, "reps": 6},
                    # cooldowns
                    {"name": "Cat-Cow Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True},
                    {"name":"Child's Pose","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Shoulder Stretch","sets":1,"duration_seconds":30,"is_cooldown":True}
                ]
            },
            # Intermediate Back Routine
            {
                "name": "Intermediate Back Routine",
                "difficulty": "intermediate",
                "muscle": "Back",
                "workouts": [
                    # warmups
                    {"name": "Jumping Jacks", "sets":1, "duration_seconds": 45, "is_warmup": True},
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 45, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 45, "is_warmup": True},
                    # main workouts
                    {"name": "Pull-ups", "sets":3, "reps": 10},
                    {"name": "Lat Pulldowns", "sets":3, "reps": 10},
                    {"name": "Barbell Rows", "sets":3, "reps": 10},
                    {"name": "Face Pulls", "sets":3, "reps": 10},
                    # cooldowns
                    {"name": "Seated Forward Bend", "sets":1, "duration_seconds": 30, "is_cooldown": True},
                    {"name":"Child's Pose","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Shoulder Stretch","sets":1,"duration_seconds":30,"is_cooldown":True}
                ]
            },
            # Advanced Back Routine
            {
                "name": "Advanced Back Routine",
                "difficulty": "advanced",
                "muscle": "Back",
                "workouts": [
                    # warmups
                    {"name": "Jumping Jacks", "sets":1, "duration_seconds": 60, "is_warmup": True},
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 60, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 60, "is_warmup": True},
                    # main workouts
                    {"name": "Weighted Pull-ups", "sets":3, "reps": 15},
                    {"name": "T-Bar Rows", "sets":3, "reps": 15},
                    {"name": "Deadlifts", "sets":3, "reps": 15},
                    {"name": "Hyperextensions", "sets":3, "reps": 15},
                    # cooldowns
                    {"name": "Seated Forward Bend", "sets":1, "duration_seconds": 30, "is_cooldown": True},
                    {"name":"Child's Pose","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Cat-Cow Stretch","sets":1,"duration_seconds":30,"is_cooldown":True}
                ]
            },
            # Elite Back Routine
            {
                "name": "Elite Back Routine",
                "difficulty": "elite",
                "muscle": "Back",
                "workouts": [
                    # warmups
                    {"name": "Jumping Jacks", "sets":1, "duration_seconds": 90, "is_warmup": True},
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 90, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 90, "is_warmup": True},
                    # main workouts
                    {"name": "Weighted Pull-ups", "sets":4, "reps": 20},
                    {"name": "T-Bar Rows", "sets":4, "reps": 20},
                    {"name": "Deadlifts", "sets":4, "reps": 20},
                    {"name": "Hyperextensions", "sets":4, "reps": 20},
                    # cooldowns
                    {"name": "Seated Forward Bend", "sets":1, "duration_seconds": 30, "is_cooldown": True},
                    {"name":"Child's Pose","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Cat-Cow Stretch","sets":1,"duration_seconds":30,"is_cooldown":True}
                ]
            },
            ### Legs Routines ###
            # Beginner Legs Routine
            {
                "name": "Beginner Legs Routine",
                "difficulty": "beginner",
                "muscle": "Legs",
                "workouts": [
                    # warmups
                    {"name": "Jumping Jacks", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "Jog in Place", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    # main workouts
                    {"name": "Squats", "sets":3, "reps": 6},
                    {"name": "Lunges", "sets":3, "reps": 6},
                    {"name": "Calf Raises", "sets":3, "reps": 6},
                    {"name": "Bulgarian Split Squats", "sets":3, "reps": 6},
                    # cooldowns
                    {"name":"Hamstring Stretch","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Quad Stretch","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Child's Pose","sets":1,"duration_seconds":30,"is_cooldown":True}
                ]
            },
            # Intermediate Legs Routine
            {
                "name": "Intermediate Legs Routine",
                "difficulty": "intermediate",
                "muscle": "Legs",
                "workouts": [
                    # warmups
                    {"name": "Jumping Jacks", "sets":1, "duration_seconds": 40, "is_warmup": True},
                    {"name": "Jog in Place", "sets":1, "duration_seconds": 40, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 40, "is_warmup": True},
                    # main workouts
                    {"name": "Squats", "sets":3, "reps": 12},
                    {"name": "Lunges", "sets":3, "reps": 12},
                    {"name": "Leg Press", "sets":3, "reps": 12},
                    {"name": "Bulgarian Split Squats", "sets":3, "reps": 12},
                    # cooldowns
                    {"name":"Hamstring Stretch","sets":1,"duration_seconds":40,"is_cooldown":True},
                    {"name":"Quad Stretch","sets":1,"duration_seconds":40,"is_cooldown":True},
                    {"name":"Child's Pose","sets":1,"duration_seconds":40,"is_cooldown":True}
                ]
            },
            # Advanced Legs Routine
            {
                "name": "Advanced Legs Routine",
                "difficulty": "advanced",
                "muscle": "Legs",
                "workouts": [
                    # warmups
                    {"name": "Jumping Jacks", "sets":1, "duration_seconds": 50, "is_warmup": True},
                    {"name": "Jog in Place", "sets":1, "duration_seconds": 50, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 50, "is_warmup": True},
                    # main workouts
                    {"name": "Barbell Squats", "sets":3, "reps": 15},
                    {"name": "Leg Extensions", "sets":3, "reps": 15},
                    {"name": "Leg Press", "sets":3, "reps": 15},
                    {"name": "Glute Bridges", "sets":3, "reps": 15},
                    # cooldowns
                    {"name":"Hamstring Stretch","sets":1,"duration_seconds":45,"is_cooldown":True},
                    {"name":"Quad Stretch","sets":1,"duration_seconds":45,"is_cooldown":True},
                    {"name":"Child's Pose","sets":1,"duration_seconds":45,"is_cooldown":True}
                ]
            },
            # Elite Legs Routine
            {
                "name": "Elite Legs Routine",
                "difficulty": "elite",
                "muscle": "Legs",
                "workouts": [
                    # warmups
                    {"name": "Jumping Jacks", "sets":1, "duration_seconds": 60, "is_warmup": True},
                    {"name": "Jog in Place", "sets":1, "duration_seconds": 60, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 60, "is_warmup": True},
                    # main workouts
                    {"name": "Barbell Squats", "sets":4, "reps": 15},
                    {"name": "Romanian Deadlifts", "sets":4, "reps": 15},
                    {"name": "Leg Extensions", "sets":4, "reps": 15},
                    {"name": "Glute Bridges", "sets":4, "reps": 15},
                    # cooldowns
                    {"name":"Hamstring Stretch","sets":1,"duration_seconds":60,"is_cooldown":True},
                    {"name":"Quad Stretch","sets":1,"duration_seconds":60,"is_cooldown":True},
                    {"name":"Child's Pose","sets":1,"duration_seconds":60,"is_cooldown":True}
                ]
            },
            ### Shoulder Routines ###
            # Beginner Shoulder Routine
            {
                "name": "Beginner Shoulder Routine",
                "difficulty": "beginner",
                "muscle": "Shoulders",
                "workouts": [
                    # warmups
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "Shoulder Rolls", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "Wrist Circles", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    # main workouts
                    {"name": "Overhead Press with Dumbbells", "sets":3, "reps": 6},
                    {"name": "Lateral Raises with Dumbbells", "sets":3, "reps": 6},
                    {"name": "Front Raises with Dumbbells", "sets":3, "reps": 6},
                    {"name": "Arnold Press with Dumbbells", "sets":3, "reps": 6},
                    # cooldowns
                    {"name":"Shoulder Stretch","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Tricep Stretch","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name": "Chest Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True}
                ]
            },
            # Intermediate Shoulder Routine
            {
                "name": "Intermediate Shoulder Routine",
                "difficulty": "intermediate",
                "muscle": "Shoulders",
                "workouts": [
                    # warmups
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 35, "is_warmup": True},
                    {"name": "Shoulder Rolls", "sets":1, "duration_seconds": 35, "is_warmup": True},
                    {"name": "Wrist Circles", "sets":1, "duration_seconds": 35, "is_warmup": True},
                    # main workouts
                    {"name": "Pike Push-ups", "sets":3, "reps": 10},
                    {"name": "Reverse Fly with Dumbbells", "sets":3, "reps": 10},
                    {"name": "Lateral Raises with Dumbbells", "sets":3, "reps": 10},
                    {"name": "Planche Leans", "sets":3, "reps": 10},
                    # cooldowns
                    {"name":"Shoulder Stretch","sets":1,"duration_seconds":35,"is_cooldown":True},
                    {"name":"Tricep Stretch","sets":1,"duration_seconds":35,"is_cooldown":True},
                    {"name": "Chest Stretch", "sets":1, "duration_seconds": 35, "is_cooldown": True}
                ]
            },
            # Advanced Shoulder Routine
            {
                "name": "Advanced Shoulder Routine",
                "difficulty": "advanced",
                "muscle": "Shoulders",
                "workouts": [
                    # warmups
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 45, "is_warmup": True},
                    {"name": "Shoulder Rolls", "sets":1, "duration_seconds": 45, "is_warmup": True},
                    {"name": "Wrist Circles", "sets":1, "duration_seconds": 45, "is_warmup": True},
                    # main workouts
                    {"name": "Advanced Pike Push-ups", "sets":3, "reps": 15},
                    {"name": "Wall Handstand Push-ups", "sets":3, "reps": 15},
                    {"name": "Lateral Raises with Dumbbells", "sets":3, "reps": 15},
                    {"name": "Planche Leans", "sets":3, "reps": 15},
                    # cooldowns
                    {"name":"Shoulder Stretch","sets":1,"duration_seconds":45,"is_cooldown":True},
                    {"name":"Tricep Stretch","sets":1,"duration_seconds":45,"is_cooldown":True},
                    {"name": "Chest Stretch", "sets":1, "duration_seconds": 45, "is_cooldown": True}
                ]
            },
            # Elite Shoulder Routine
            {
                "name": "Elite Shoulder Routine",
                "difficulty": "elite",
                "muscle": "Shoulders",
                "workouts": [
                    # warmups
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 60, "is_warmup": True},
                    {"name": "Shoulder Rolls", "sets":1, "duration_seconds": 60, "is_warmup": True},
                    {"name": "Wrist Circles", "sets":1, "duration_seconds": 60, "is_warmup": True},
                    # main workouts
                    {"name": "Wall Handstand Push-ups", "sets":3, "reps": 20},
                    {"name": "Handstand Hold", "sets":3, "duration_seconds": 60},
                    {"name": "Lateral Raises with Dumbbells", "sets":3, "reps": 20},
                    {"name": "Planche Leans", "sets":3, "reps": 20},
                    # cooldowns
                    {"name":"Shoulder Stretch","sets":1,"duration_seconds":60,"is_cooldown":True},
                    {"name":"Tricep Stretch","sets":1,"duration_seconds":60,"is_cooldown":True},
                    {"name": "Chest Stretch", "sets":1, "duration_seconds": 60, "is_cooldown": True}
                ]
            },
            ### Arms Routines ###
            # Beginner Arms Routine
            {
                "name": "Beginner Arms Routine",
                "difficulty": "beginner",
                "muscle": "Arms",
                "workouts": [
                    # warmups
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "Shoulder Rolls", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "Wrist Circles", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    # main workouts
                    {"name": "Bicep Curls with Dumbbells", "sets":3, "reps": 6},
                    {"name": "Tricep Dips", "sets":3, "reps": 6},
                    {"name": "Hammer Curls with Dumbbells", "sets":3, "reps": 6},
                    {"name": "Diamond Push-ups", "sets":3, "reps": 6},
                    # cooldowns
                    {"name":"Shoulder Stretch","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Tricep Stretch","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name": "Bicep Stretch", "sets":1, "duration_seconds": 30, "is_cooldown": True}
                ]
            },
            # Intermediate Arms Routine
            {
                "name": "Intermediate Arms Routine",
                "difficulty": "intermediate",
                "muscle": "Arms",
                "workouts": [
                    # warmups
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 35, "is_warmup": True},
                    {"name": "Shoulder Rolls", "sets":1, "duration_seconds": 35, "is_warmup": True},
                    {"name": "Wrist Circles", "sets":1, "duration_seconds": 35, "is_warmup": True},
                    # main workouts
                    {"name": "Bicep Curls with Dumbbells", "sets":3, "reps": 12},
                    {"name": "Tricep Kickbacks with Dumbbells", "sets":3, "reps": 12},
                    {"name": "Hammer Curls with Dumbbells", "sets":3, "reps": 12},
                    {"name": "Diamond Push-ups", "sets":3, "reps": 12},
                    # cooldowns
                    {"name":"Shoulder Stretch","sets":1,"duration_seconds":35,"is_cooldown":True},
                    {"name":"Tricep Stretch","sets":1,"duration_seconds":35,"is_cooldown":True},
                    {"name": "Bicep Stretch", "sets":1, "duration_seconds": 35, "is_cooldown": True}
                ]
            },
            # Advanced Arms Routine
            {
                "name": "Advanced Arms Routine",
                "difficulty": "advanced",
                "muscle": "Arms",
                "workouts": [
                    # warmups
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 45, "is_warmup": True},
                    {"name": "Shoulder Rolls", "sets":1, "duration_seconds": 45, "is_warmup": True},
                    {"name": "Wrist Circles", "sets":1, "duration_seconds": 45, "is_warmup": True},
                    # main workouts
                    {"name": "Zottman Curls with Dumbbells", "sets":3, "reps": 15},
                    {"name": "Skull Crushers with Dumbbells", "sets":3, "reps": 15},
                    {"name": "Hammer Curls with Dumbbells", "sets":3, "reps": 15},
                    {"name": "Diamond Push-ups", "sets":3, "reps": 20},
                    # cooldowns
                    {"name":"Shoulder Stretch","sets":1,"duration_seconds":45,"is_cooldown":True},
                    {"name":"Tricep Stretch","sets":1,"duration_seconds":45,"is_cooldown":True},
                    {"name": "Bicep Stretch", "sets":1, "duration_seconds": 45, "is_cooldown": True}
                ]
            },
            # Elite Arms Routine
            {
                "name": "Elite Arms Routine",
                "difficulty": "elite",
                "muscle": "Arms",
                "workouts": [
                    # warmups
                    {"name": "Arm Circles", "sets":1, "duration_seconds": 60, "is_warmup": True},
                    {"name": "Shoulder Rolls", "sets":1, "duration_seconds": 60, "is_warmup": True},
                    {"name": "Wrist Circles", "sets":1, "duration_seconds": 60, "is_warmup": True},
                    # main workouts
                    {"name": "Concentration Curls with Dumbbells", "sets":4, "reps": 15},
                    {"name": "Skull Crushers with Dumbbells", "sets":4, "reps": 15},
                    {"name": "Hammer Curls with Dumbbells", "sets":4, "reps": 15},
                    {"name": "Diamond Push-ups", "sets":4, "reps": 25},
                    # cooldowns
                    {"name":"Shoulder Stretch","sets":1,"duration_seconds":60,"is_cooldown":True},
                    {"name":"Tricep Stretch","sets":1,"duration_seconds":60,"is_cooldown":True},
                    {"name": "Bicep Stretch", "sets":1, "duration_seconds": 60, "is_cooldown": True}
                ]
            },
            ### Core Routines ###
            # Beginner Core Routine
            {
                "name": "Beginner Core Routine",
                "difficulty": "beginner",
                "muscle": "Core",
                "workouts": [
                    # warmups
                    {"name": "Hamstring Stretch", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "Hip Flexor Stretch", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    # main workouts
                    {"name": "Russian Twists", "sets":3, "reps": 10},
                    {"name": "Leg Raises", "sets":3, "reps": 10},
                    {"name": "Bicycle Crunches", "sets":3, "reps": 10},
                    {"name": "Plank", "sets":3, "duration_seconds": 30},
                    # cooldowns
                    {"name":"Child's Pose","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Cat-Cow Stretch","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Seated Forward Bend","sets":1,"duration_seconds":30,"is_cooldown":True}
                ]
            },
             # Intermediate Core Routine
            {
                "name": "Intermediate Core Routine",
                "difficulty": "intermediate",
                "muscle": "Core",
                "workouts": [
                    # warmups
                    {"name": "Hamstring Stretch", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "Hip Flexor Stretch", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    # main workouts
                    {"name": "Mountain Climbers", "sets":3, "reps": 15},
                    {"name": "Bicycle Crunches", "sets":3, "reps": 15},
                    {"name": "Leg Raises", "sets":3, "reps": 15},
                    {"name": "Plank", "sets":3, "duration_seconds": 45},
                    # cooldowns
                    {"name":"Child's Pose","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Cat-Cow Stretch","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Seated Forward Bend","sets":1,"duration_seconds":30,"is_cooldown":True}
                ]
            },
             # Advanced Core Routine
            {
                "name": "Advanced Core Routine",
                "difficulty": "advanced",
                "muscle": "Core",
                "workouts": [
                    # warmups
                    {"name": "Hamstring Stretch", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "Hip Flexor Stretch", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    # main workouts
                    {"name": "V-Ups", "sets":3, "reps": 20},
                    {"name": "Mountain Climbers", "sets":3, "reps": 30},
                    {"name": "Hanging Leg Raises", "sets":3, "reps": 20},
                    {"name": "Plank", "sets":3, "duration_seconds": 60},
                    # cooldowns
                    {"name":"Child's Pose","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Cat-Cow Stretch","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Seated Forward Bend","sets":1,"duration_seconds":30,"is_cooldown":True}
                ]
            },
             # Elite Core Routine
            {
                "name": "Elite Core Routine",
                "difficulty": "elite",
                "muscle": "Core",
                "workouts": [
                    # warmups
                    {"name": "Hamstring Stretch", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "Hip Flexor Stretch", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    {"name": "High Knees", "sets":1, "duration_seconds": 30, "is_warmup": True},
                    # main workouts
                    {"name": "V-Ups", "sets":3, "reps": 25},
                    {"name": "Ab Wheel Rollouts", "sets":3, "reps": 45},
                    {"name": "Dragon Flags", "sets":3, "reps": 20},
                    {"name": "Hanging Leg Raises", "sets":3, "reps": 25},
                    # cooldowns
                    {"name":"Child's Pose","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Cat-Cow Stretch","sets":1,"duration_seconds":30,"is_cooldown":True},
                    {"name":"Seated Forward Bend","sets":1,"duration_seconds":30,"is_cooldown":True}
                ]
            }
        ]

        def get_workout_id(db, name):
            workouts = db.exec(select(Workout)).all()

            for w in workouts:
                if w.name.lower() == name.lower():
                    return w.id
            return None
        
        for r in routine_data:
            routine = Routine(
                name=r["name"],
                difficulty=r["difficulty"],
                user_id=bob_db.id,
                is_generated= False,
                creation_date=date.today()
            )
            db.add(routine)
            db.commit()
            db.refresh(routine)

            order = 1

            for workout in r["workouts"]:
                workout_id = get_workout_id(db, workout["name"])

                if workout_id is not None:
                    routine_workout = RoutineWorkout(
                        routine_id=routine.id,
                        workout_id=workout_id,
                        difficulty=r["difficulty"],
                        order_in_routine=order,
                        sets=workout.get("sets"),
                        reps=workout.get("reps"),
                        is_warmup=workout.get("is_warmup", False),
                        is_cooldown=workout.get("is_cooldown", False)
                    )
                    db.add(routine_workout)
                    order += 1
            db.commit()

        print("Database Initialized")

@cli.command()
def test():
    print("You're already in the test")


if __name__ == "__main__":
    cli()