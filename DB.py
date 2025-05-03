import sqlite3
import os
from datetime import datetime

def create_database():
    # Check if database file exists, if not create it
    db_file = 'workout_tracker.db'
    # connecting to sql
    conn = sqlite3.connect(db_file)
    # object for connection to retrieve data from db
    cursor = conn.cursor()
    # create table for workouts
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workouts (
        workout_id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_date DATE NOT NULL,
        workout_name TEXT NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    # create table for exercises
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercises (
        exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_name TEXT NOT NULL UNIQUE,
        exercise_category TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workout_exercises (
        workout_exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER NOT NULL,
        exercise_id INTEGER NOT NULL,
        order_index INTEGER NOT NULL,
        notes TEXT,
        FOREIGN KEY (workout_id) REFERENCES workouts (workout_id),
        FOREIGN KEY (exercise_id) REFERENCES exercises (exercise_id)
    )
    ''')
    # create table for sets
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercise_sets (
        set_id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_exercise_id INTEGER NOT NULL,
        set_number INTEGER NOT NULL,
        reps INTEGER,
        weight REAL,
        duration INTEGER,  
        distance REAL,     
        completed BOOLEAN DEFAULT 1,
        notes TEXT,
        FOREIGN KEY (workout_exercise_id) REFERENCES workout_exercises (workout_exercise_id)
    )
    ''')
    conn.commit()
    default_exercises = [
        ('Bench Press', 'Chest'),
        ('Incline Dumbbell Press', 'Chest'),
        ('Decline Barbell Press', 'Lower Chest'),
        ('Flyes (Dumbbell/Cable)', 'Chest'),
        ('Squat', 'Legs'),
        ('Front Squat', 'Quads'),
        ('Leg Press', 'Quads'),
        ('Hamstring Curl', 'Hamstrings'),
        ('Leg Extension', 'Quads'),
        ('Calf Raises', 'Calves'),
        ('Deadlift', 'Back'),
        ('Romanian Deadlift (RDL)', 'Hamstrings, Glutes'),
        ('Bent-Over Rows (Barbell/Dumbbell)', 'Back'),
        ('Seated Cable Rows', 'Back'),
        ('Lat Pulldowns', 'Back'),
        ('Pull-up', 'Back'),
        ('Chin-up', 'Biceps, Back'),
        ('Push-up', 'Chest, Triceps, Shoulders'),
        ('Dips', 'Triceps, Chest, Shoulders'),
        ('Overhead Press (Barbell/Dumbbell)', 'Shoulders'),
        ('Lateral Raises', 'Shoulders'),
        ('Front Raises', 'Shoulders'),
        ('Rear Delt Flyes', 'Shoulders'),
        ('Bicep Curl (Barbell/Dumbbell)', 'Biceps'),
        ('Hammer Curls', 'Biceps, Forearms'),
        ('Concentration Curls', 'Biceps'),
        ('Triceps Pushdown (Cable)', 'Triceps'),
        ('Overhead Triceps Extension', 'Triceps'),
        ('Skullcrushers', 'Triceps'),
        ('Plank', 'Core'),
        ('Crunches', 'Abs'),
        ('Leg Raises', 'Lower Abs'),
        ('Russian Twists', 'Obliques'),
        ('Bird Dog', 'Core, Back'),
        ('Running', 'Cardio'),
        ('Cycling', 'Cardio'),
        ('Swimming', 'Cardio, Full Body'),
        ('Jumping Jacks', 'Cardio, Full Body'),
        ('Burpees', 'Cardio, Full Body'),
        ('Lunges', 'Legs, Glutes'),
        ('Step-ups', 'Legs, Glutes'),
        ('Glute Bridges', 'Glutes'),
        ('Good Mornings', 'Hamstrings, Glutes, Lower Back'),
        ('Face Pulls', 'Upper Back, Shoulders'),
        ('Shrugs (Barbell/Dumbbell)', 'Traps'),
        ("Farmer's Walk", 'Full Body, Grip'),
        ('Medicine Ball Slams', 'Core, Full Body'),
        ('Kettlebell Swings', 'Full Body, Glutes, Hamstrings')
    ]
    # Insert default exercises into the exercises table
    cursor.executemany(
        'INSERT OR IGNORE INTO exercises (name, category) VALUES (?, ?)',
        default_exercises
    )
    conn.commit()
    conn.close()
    print(f"Database created successfully at {db_file}")

class WorkoutDatabase:
    def __init__(self, db_path='workout_tracker.db'):
        self.db_path = db_path
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
        
    def add_workout(self, workout_date, workout_name, notes=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO workouts (workout_date, workout_name, notes)
        VALUES (?, ?, ?)
        ''', (workout_date, workout_name, notes))
        
        workout_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return workout_id
        
    def add_exercise_to_workout(self, workout_id, exercise_id, order_index, notes=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO workout_exercises (workout_id, exercise_id, order_index, notes)
        VALUES (?, ?, ?, ?)
        ''', (workout_id, exercise_id, order_index, notes))
        
        workout_exercise_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return workout_exercise_id
        
    def add_set(self, workout_exercise_id, set_number, reps=None, weight=None, 
                duration=None, distance=None, completed=True, notes=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO exercise_sets 
        (workout_exercise_id, set_number, reps, weight, duration, distance, completed, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (workout_exercise_id, set_number, reps, weight, duration, distance, completed, notes))
        
        set_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return set_id
        
    def get_all_workouts(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM workouts 
        ORDER BY workout_date DESC
        ''')
        
        workouts = cursor.fetchall()
        conn.close()
        return workouts
    
    def get_workout_details(self, workout_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get workout info
        cursor.execute('SELECT * FROM workouts WHERE workout_id = ?', (workout_id,))
        workout = cursor.fetchone()
        
        # Get exercises for this workout
        cursor.execute('''
        SELECT we.workout_exercise_id, e.name, e.category, we.notes 
        FROM workout_exercises we
        JOIN exercises e ON we.exercise_id = e.exercise_id
        WHERE we.workout_id = ?
        ORDER BY we.order_index
        ''', (workout_id,))
        
        exercises = cursor.fetchall()
        
        # Get sets for each exercise
        workout_details = {
            'workout': dict(workout),
            'exercises': []
        }
        
        for exercise in exercises:
            exercise_dict = dict(exercise)
            
            cursor.execute('''
            SELECT * FROM exercise_sets 
            WHERE workout_exercise_id = ?
            ORDER BY set_number
            ''', (exercise['workout_exercise_id'],))
            
            sets = cursor.fetchall()
            exercise_dict['sets'] = [dict(s) for s in sets]
            workout_details['exercises'].append(exercise_dict)
        
        conn.close()
        return workout_details
        
    def update_set(self, set_id, set_number=None, reps=None, weight=None, 
                  duration=None, distance=None, completed=None, notes=None):
        conn = self.get_connection()
        cursor = conn.cursor()
    
        # Check if set exists
        cursor.execute('SELECT set_id FROM exercise_sets WHERE set_id = ?', (set_id,))
        if not cursor.fetchone():
            conn.close()
            return False
    
        # Build the update query dynamically
        updates = []
        values = []
    
        if set_number is not None:
            updates.append("set_number = ?")
            values.append(set_number)
        if reps is not None:
            updates.append("reps = ?")
            values.append(reps)
        if weight is not None:
            updates.append("weight = ?")
            values.append(weight)
        if duration is not None:
            updates.append("duration = ?")
            values.append(duration)
        if distance is not None:
            updates.append("distance = ?")
            values.append(distance)
        if completed is not None:
            updates.append("completed = ?")
            values.append(completed)
        if notes is not None:
            updates.append("notes = ?")
            values.append(notes)
    
        if not updates:
            conn.close()
            return True  # Nothing to update
    
        # Create the SQL query
        sql = f"UPDATE exercise_sets SET {', '.join(updates)} WHERE set_id = ?"
        values.append(set_id)
    
        # Execute the query
        cursor.execute(sql, values)
    
        conn.commit()
        conn.close()
        return True
        
    def delete_set(self, set_id):
        conn = self.get_connection()
        cursor = conn.cursor()
    
        # Check if set exists
        cursor.execute('SELECT set_id FROM exercise_sets WHERE set_id = ?', (set_id,))
        if not cursor.fetchone():
            conn.close()
            return False
    
        # Delete the set
        cursor.execute('DELETE FROM exercise_sets WHERE set_id = ?', (set_id,))
    
        conn.commit()
        conn.close()
        return True
        
    def get_all_exercises(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM exercises ORDER BY name')
        
        exercises = cursor.fetchall()
        conn.close()
        return exercises

    def add_exercise(self, name, category=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO exercises (name, category) VALUES (?, ?)',
            (name, category)
        )
        
        exercise_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return exercise_id

    def delete_workout(self, workout_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if workout exists
        cursor.execute('SELECT workout_id FROM workouts WHERE workout_id = ?', (workout_id,))
        if not cursor.fetchone():
            conn.close()
            return False
        
        # Delete associated sets first
        cursor.execute('''
        DELETE FROM exercise_sets 
        WHERE workout_exercise_id IN (
            SELECT workout_exercise_id FROM workout_exercises WHERE workout_id = ?
        )
        ''', (workout_id,))
        
        # Delete workout exercises
        cursor.execute('DELETE FROM workout_exercises WHERE workout_id = ?', (workout_id,))
        
        # Delete the workout
        cursor.execute('DELETE FROM workouts WHERE workout_id = ?', (workout_id,))
        
        conn.commit()
        conn.close()
        return True

    def delete_workout_exercise(self, workout_exercise_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if workout exercise exists
        cursor.execute(
            'SELECT workout_exercise_id FROM workout_exercises WHERE workout_exercise_id = ?', 
            (workout_exercise_id,)
        )
        if not cursor.fetchone():
            conn.close()
            return False
        
        # Delete associated sets first
        cursor.execute(
            'DELETE FROM exercise_sets WHERE workout_exercise_id = ?', 
            (workout_exercise_id,)
        )
        
        # Delete the workout exercise
        cursor.execute(
            'DELETE FROM workout_exercises WHERE workout_exercise_id = ?', 
            (workout_exercise_id,)
        )
        
        conn.commit()
        conn.close()
        return True    

def test_database():
    db = WorkoutDatabase()
    
    # Add a test workout
    workout_date = datetime.now().strftime('%Y-%m-%d')
    workout_id = db.add_workout(workout_date, 'Morning Strength Training', 
                               'Felt good today, increased bench press weight')
    
    # Add exercises to the workout
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get bench press id
    cursor.execute('SELECT exercise_id FROM exercises WHERE name = ?', ('Bench Press',))
    bench_press_id = cursor.fetchone()['exercise_id']
    
    # Get squat id
    cursor.execute('SELECT exercise_id FROM exercises WHERE name = ?', ('Calf Raises',))
    squat_id = cursor.fetchone()['exercise_id']
    
    conn.close()
    
    # Add bench press to workout
    bench_press_we_id = db.add_exercise_to_workout(workout_id, bench_press_id, 1)
    
    # Add sets for bench press
    db.add_set(bench_press_we_id, 1, reps=10, weight=135)
    db.add_set(bench_press_we_id, 2, reps=8, weight=155)
    db.add_set(bench_press_we_id, 3, reps=6, weight=175)
    
    # Add squat to workout
    squat_we_id = db.add_exercise_to_workout(workout_id, squat_id, 2)
    
    # Add sets for squat
    db.add_set(squat_we_id, 1, reps=10, weight=185)
    db.add_set(squat_we_id, 2, reps=10, weight=205)
    db.add_set(squat_we_id, 3, reps=8, weight=225)
    
    # Test retrieving the workout
    workout_details = db.get_workout_details(workout_id)
    print(f"Created workout: {workout_details['workout']['workout_name']}")
    print(f"Date: {workout_details['workout']['workout_date']}")
    print(f"Exercises: {len(workout_details['exercises'])}")
    
    for exercise in workout_details['exercises']:
        print(f"- {exercise['name']}: {len(exercise['sets'])} sets")
        for set_info in exercise['sets']:
            print(f"  * Set {set_info['set_number']}: {set_info['set_number']} reps at {set_info['weight']} lbs")
    
    print("\nTest complete!")