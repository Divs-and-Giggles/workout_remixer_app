import csv
from pathlib import Path
from sqlmodel import Session, select
from app.database import get_cli_session, create_db_and_tables, drop_all
from app.models.workout import Workout, MuscleGroup, User
from app.models.other import WorkoutMuscle, WorkoutGif, SecondaryMuscles
from app.utilities.security import encrypt_password

def initialize():
        
    with get_cli_session() as db:
        drop_all()
        create_db_and_tables()
        # Read CSV and populate
            
        bob = User(username='bob', email='bob@mail.com', password=encrypt_password("bobpass"))
        db.add(bob)
        
        mg1 = MuscleGroup(name="abductors")
        mg2 = MuscleGroup(name="abs")
        mg3 = MuscleGroup(name="adductors")
        mg4 = MuscleGroup(name="biceps")
        mg5 = MuscleGroup(name="calves")
        mg6 = MuscleGroup(name="cardiovascular system")
        mg7 = MuscleGroup(name="delts")
        mg8 = MuscleGroup(name="forearms")
        mg9 = MuscleGroup(name="glutes")
        mg10 = MuscleGroup(name="hamstrings")
        mg11 = MuscleGroup(name="lats")
        mg12 = MuscleGroup(name="levator scapulae")
        mg13 = MuscleGroup(name="pectorals")
        mg14 = MuscleGroup(name="quads")
        mg15 = MuscleGroup(name="serratus anterior")
        mg16 = MuscleGroup(name="spine")
        mg17 = MuscleGroup(name="traps")
        mg18 = MuscleGroup(name="triceps")
        mg19 = MuscleGroup(name="upper back")
        
        musclegroups = [mg1, mg2, mg3, mg4, mg5, mg6, mg7, mg8, mg9, mg10, mg11, mg12, mg13, mg14, mg15, mg16, mg17, mg18, mg19]
        
        for mg in musclegroups:
            db.add(mg)
        db.commit() 
           
        with open('exercises_matched.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                workout = Workout(
                        name= str(row['Name']),
                        difficulty=str(row['Difficulty']),
                        workout_type=str(row['WorkoutType']),
                        equipment=str(row['Equipment']),
                        intensity=float(row['Intensity']),
                        instructions=str(row['Instructions'])
                    )
                db.add(workout)
                db.commit()
                db.refresh(workout)
                
                secondary = str(row['Secondary Muscles'])
                if secondary:
                    sm = SecondaryMuscles(workout_id=workout.id, muscles=secondary)
                    db.add(sm)
                
                musclegroup = db.exec(select(MuscleGroup).where(MuscleGroup.name == str(row['Target']))).one_or_none()
                if  musclegroup: 
                    wm = WorkoutMuscle(muscle_group_id=musclegroup.id, workout_id=workout.id)
                    db.add(wm)
                else:
                    print(f"Muscle group {row['Target']} not found")
                    
                wg= WorkoutGif(workout_id=workout.id, name=str(row['Name']), gif_url=str(row['gifID']))
                db.add(wg)
        db.commit()        
        
    print("Database initialized")
if __name__ == "__main__":
    initialize()