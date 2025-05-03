# main.py
import os
from DB import WorkoutDatabase, create_database, test_database
from api import start_api_server

def main():
    print("Starting Workout Tracker application...")
    
    # Check if database exists, create it if not
    db_file = 'workout_tracker.db'
    if not os.path.exists(db_file):
        print("Database not found. Creating new database...")
        create_database()
    else:
        print(f"Database found at {db_file}")
    
    # Initialize database connection
    db = WorkoutDatabase()
    
    # Print some stats from the database
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM workouts")
    workout_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM exercises")
    exercise_count = cursor.fetchone()['count']
    
    conn.close()
    
    print(f"Database contains {workout_count} workouts and {exercise_count} exercises")
    
    # Start the API server
    print("Starting API server...")
    print("API will be available at http://127.0.0.1:8000")
    print("Documentation available at http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    # Start the API server (this will block until the server is stopped)
    start_api_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped by user")