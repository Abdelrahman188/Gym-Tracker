# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import uvicorn

# your database wrapper
from DB import WorkoutDatabase

app = FastAPI(title="Workout Tracker API")
db = WorkoutDatabase()


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"status": "Workout Tracker API is running"}


#
# Pydantic models
#

class WorkoutBase(BaseModel):
    workout_date: date
    workout_name: str
    notes: Optional[str] = None


class WorkoutCreate(WorkoutBase):
    pass


class Workout(WorkoutBase):
    workout_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ExerciseBase(BaseModel):
    """Base Pydantic model for exercise data"""
    exercise_name: str
    exercise_category: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    """Pydantic model for creating a new exercise"""
    # Inherits all fields from ExerciseBase
    pass

class Exercise(ExerciseBase):
    """Pydantic model for a complete exercise with ID"""
    exercise_id: int
    
    class Config:
        orm_mode = True


class SetBase(BaseModel):
    set_number: int
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration: Optional[int] = None
    distance: Optional[float] = None
    completed: bool = True
    notes: Optional[str] = None


class SetCreate(SetBase):
    pass


class Set(SetBase):
    set_id: int

    class Config:
        orm_mode = True


class WorkoutExerciseCreate(BaseModel):
    exercise_id: int
    order_index: int
    notes: Optional[str] = None
    sets: List[SetCreate]


class WorkoutDetail(BaseModel):
    workout: Workout
    exercises: List[Dict[str, Any]]  # expecting each to be {"exercise": Exercise, "sets": List[Set]}


#
# Workout endpoints
#

@app.get("/workouts", response_model=List[Workout])
def get_workouts():
    records = db.get_all_workouts()
    return[dict(workout)for workout in records]


@app.get("/workouts/{workout_id}", response_model=WorkoutDetail)
def get_workout(workout_id: int):
    details = db.get_workout_details(workout_id)
    if not details:
        raise HTTPException(status_code=404, detail="Workout not found")
    return details


@app.post("/workouts", response_model=Dict[str, Any])
def create_workout(workout: WorkoutCreate):
    wid = db.add_workout(
        workout_date=workout.workout_date,
        workout_name=workout.workout_name,
        notes=workout.notes,
    )
    return {"workout_id": wid, **workout.model_dump()}


@app.delete("/workouts/{workout_id}", response_model=Dict[str, str])
def delete_workout(workout_id: int):
    success = db.delete_workout(workout_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"message": "Workout deleted successfully"}


#
# Exercise endpoints
#

@app.get("/exercises", response_model=List[Exercise])
def get_exercises():
    records = db.get_all_exercises()
    return [
        {
            "exercise_id": record["exercise_id"],
            "exercise_name": record["name"],
            "exercise_category": record["category"]
        }
        for record in records
    ]

@app.post("/exercises", response_model=Exercise)
def create_exercise(exercise: ExerciseCreate):
    eid = db.add_exercise(
        exercise_name=exercise.exercise_name,
        exercise_category=exercise.exercise_category,
    )
    return Exercise(exercise_id=eid, **exercise.model_dump())


#
# Link exercises & sets to workouts
#

@app.post("/workouts/{workout_id}/exercises", response_model=Dict[str, int])
def add_exercise_to_workout(workout_id: int, data: WorkoutExerciseCreate):
    weid = db.add_exercise_to_workout(
        workout_id=workout_id,
        exercise_id=data.exercise_id,
        order_index=data.order_index,
        notes=data.notes,
    )
    for s in data.sets:
        db.add_set(
            workout_exercise_id=weid,
            set_number=s.set_number,
            reps=s.reps,
            weight=s.weight,
            duration=s.duration,
            distance=s.distance,
            completed=s.completed,
            notes=s.notes,
        )
    return {"workout_exercise_id": weid}


@app.delete("/workout-exercises/{workout_exercise_id}", response_model=Dict[str, str])
def delete_workout_exercise(workout_exercise_id: int):
    success = db.delete_workout_exercise(workout_exercise_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workout exercise not found")
    return {"message": "Exercise removed from workout successfully"}


@app.post("/workout-exercises/{workout_exercise_id}/sets", response_model=Dict[str, Any])
def add_set(workout_exercise_id: int, set_data: SetCreate):
    sid = db.add_set(
        workout_exercise_id=workout_exercise_id,
        set_number=set_data.set_number,
        reps=set_data.reps,
        weight=set_data.weight,
        duration=set_data.duration,
        distance=set_data.distance,
        completed=set_data.completed,
        notes=set_data.notes,
    )
    return {"set_id": sid, **set_data.model_dump()}


@app.put("/sets/{set_id}", response_model=Dict[str, str])
def update_set(set_id: int, set_data: SetBase):
    success = db.update_set(
        set_id=set_id,
        set_number=set_data.set_number,
        reps=set_data.reps,
        weight=set_data.weight,
        duration=set_data.duration,
        distance=set_data.distance,
        completed=set_data.completed,
        notes=set_data.notes,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Set not found")
    return {"message": "Set updated successfully"}


@app.delete("/sets/{set_id}", response_model=Dict[str, str])
def delete_set(set_id: int):
    success = db.delete_set(set_id)
    if not success:
        raise HTTPException(status_code=404, detail="Set not found")
    return {"message": "Set deleted successfully"}


def start_api_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    # Launch server in background and then run a quick smoke-test
    import threading
    import time
    import requests

    threading.Thread(target=start_api_server, daemon=True).start()
    time.sleep(1)  # give Uvicorn a moment to start

    # Smoke-tests
    print("Health check:", requests.get("http://127.0.0.1:8000/").json())
    test_workout = {
        "workout_date": "2025-04-24",
        "workout_name": "Test Workout",
        "notes": "API test"
    }
    print("Create workout:", requests.post("http://127.0.0.1:8000/workouts", json=test_workout).json())
    print("List workouts:", requests.get("http://127.0.0.1:8000/workouts").json())
