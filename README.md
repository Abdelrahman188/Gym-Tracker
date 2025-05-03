# Workout Tracker Application

This is a full-stack Workout Tracker application consisting of a FastAPI backend to manage workout data and a PyQt5 frontend for a user-friendly desktop interface.  It allows users to log, track, and analyze their workouts.

## Table of Contents

1.  [  **Introduction** ](#introduction)
2.  [  **Features** ](#features)
3.  [  **Getting Started** ](#getting-started)
    * [  Prerequisites  ](#prerequisites)
    * [  Installation  ](#installation)
    * [  Database Setup  ](#database-setup)
    * [  Running the API  ](#running-the-api)
    * [  Running the Frontend  ](#running-the-frontend-1)
4.  [  **API Endpoints** ](#api-endpoints)
    * [  Workouts  ](#workouts)
    * [  Exercises  ](#exercises)
    * [  Workout Exercises and Sets  ](#workout-exercises-and-sets)
5.  [  **Pydantic Models** ](#pydantic-models)
6.  [  **Database Schema** ](#database-schema)
7.  [  **Frontend** ](#frontend)
    * [  Overview  ](#frontend-overview)
    * [  Key Widgets and Pages  ](#key-widgets-and-pages)
    * [  Running the Frontend  ](#running-the-frontend-1)
    * [  Frontend Dependencies  ](#frontend-dependencies)
8.  [  **API Client** ](#api-client)
9.  [  **Testing** ](#testing)
10. [  **Contributing** ](#contributing)
11. [  **License** ](#license)

## Introduction

The Workout Tracker application provides a comprehensive solution for managing workout routines. The backend, built with FastAPI, handles data storage and retrieval using SQLite. The PyQt5 frontend offers an intuitive desktop interface for users to interact with their workout data.

## Features

* **Workout Management:** Create, retrieve, update, and delete workout records via both the API and the frontend.
* **Exercise Management:** Create and retrieve exercises through the API, accessible in the frontend. The backend is pre-populated with a wide range of default exercises.
* **Set Management:** Log sets for each exercise, including details like reps, weight, duration, and distance.
* **Workout History:** View past workouts, track progress, and analyze performance.
* **Data Persistence:** SQLite database ensures data is saved locally.
* **API Documentation:** FastAPI automatically generates Swagger UI for easy API exploration.
* **User-Friendly Interface:** PyQt5 frontend provides a rich, interactive experience.

## Getting Started

### Prerequisites

* Python 3.7+
* pip (Python package installer)

### Installation

1.  Clone the repository:

    ```bash
    git clone <your-repository-url>
    cd your-repository-name
    ```

2.  It is recommended to create a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\\Scripts\\activate  # On Windows
    ```

3.  Install the backend dependencies:

    ```bash
    pip install fastapi uvicorn python-dateutil
    ```

4.  Install the frontend dependencies:

    ```bash
    pip install PyQt5 requests matplotlib
    ```

### Database Setup

The application automatically creates the SQLite database file (`workout_tracker.db`) if it doesn't exist. The `create_database()` function in `DB.py` handles the database creation and schema setup. It also pre-populates the `exercises` table with a comprehensive list of common exercises.

### Running the API

1.  Start the FastAPI backend:

    ```bash
    python api.py
    ```

2.  The API will be accessible at `http://127.0.0.1:8000`.

3.  Explore the API documentation at `http://127.0.0.1:8000/docs`.

### Running the Frontend

1.  Ensure the FastAPI backend is running.
2.  Launch the PyQt5 frontend:

    ```bash
    python main.py  # or python main_window.py
    ```

## API Endpoints

The Workout Tracker API provides the following endpoints:

### Workouts

* **`GET /workouts`**

    * Retrieves a list of all workouts.
    * Response Model: `List[Workout]`
    * Example Response:

        ```json
        [
          {
            "workout_id": 1,
            "workout_date": "2024-07-26",
            "workout_name": "Leg Day",
            "notes": "Heavy squats and deadlifts",
            "created_at": "2024-07-26T10:00:00"
          },
          {
            "workout_id": 2,
            "workout_date": "2024-07-27",
            "workout_name": "Chest and Triceps",
            "notes": "Bench press focus",
            "created_at": "2024-07-27T12:00:00"
          }
        ]
        ```

* **`GET /workouts/{workout_id}`**

    * Retrieves details for a specific workout, including its exercises and sets.
    * Path Parameters:
        * `workout_id` (int): The ID of the workout to retrieve.
    * Response Model: `WorkoutDetail`
    * Raises: `HTTPException` (status\_code=404) if the workout is not found.
    * Example Response:

        ```json
        {
          "workout": {
            "workout_id": 1,
            "workout_date": "2024-07-26",
            "workout_name": "Leg Day",
            "notes": "Heavy squats and deadlifts",
            "created_at": "2024-07-26T10:00:00"
          },
          "exercises": [
            {
              "exercise": {
                "exercise_id": 5,
                "exercise_name": "Squat",
                "exercise_category": "Legs"
              },
              "sets": [
                {
                  "set_id": 1,
                  "workout_exercise_id": 1,
                  "set_number": 1,
                  "reps": 10,
                  "weight": 185.0,
                  "duration": null,
                  "distance": null,
                  "completed": true,
                  "notes": null
                },
                {
                  "set_id": 2,
                  "workout_exercise_id": 1,
                  "set_number": 2,
                  "reps": 10,
                  "weight": 205.0,
                  "duration": null,
                  "distance": null,
                  "completed": true,
                  "notes": null
                }
              ]
            }
          ]
        }
        ```

* **`POST /workouts`**

    * Creates a new workout.
    * Request Body: `WorkoutCreate`
    * Response Model: `Dict[str, Any]` (includes the new workout's ID)
    * Example Request:

        ```json
        {
          "workout_date": "2024-07-28",
          "workout_name": "Full Body",
          "notes": "General conditioning"
        }
        ```

    * Example Response:

        ```json
        {
          "workout_id": 3
        }
        ```

* **`DELETE /workouts/{workout_id}`**

    * Deletes a specific workout.
    * Path Parameters:
        * `workout_id` (int): The ID of the workout to delete.
    * Response Model: `Dict[str, str]` ({"message": "Workout deleted successfully"})
    * Raises: `HTTPException` (status\_code=404) if the workout is not found.

### Exercises

* **`GET /exercises`**

    * Retrieves a list of all exercises.
    * Response Model: `List[Exercise]`
    * Example Response:

        ```json
        [
          {
            "exercise_id": 1,
            "exercise_name": "Bench Press",
            "exercise_category": "Chest"
          },
          {
            "exercise_id": 2,
            "exercise_name": "Squat",
            "exercise_category": "Legs"
          },
          ...
        ]
        ```

* **`POST /exercises`**

    * Creates a new exercise.
    * Request Body: `ExerciseCreate`
    * Response Model: `Exercise`
    * Example Request:

        ```json
        {
          "exercise_name": "Pull-up",
          "exercise_category": "Back"
        }
        ```

    * Example Response:

        ```json
        {
          "exercise_id": 48,
          "exercise_name": "Pull-up",
          "exercise_category": "Back"
        }
        ```

### Workout Exercises and Sets

* **`POST /workouts/{workout_id}/exercises`**

    * Adds an exercise to a specific workout, including its sets.
    * Path Parameters:
        * `workout_id` (int): The ID of the workout.
    * Request Body: `WorkoutExerciseCreate`
    * Response Model: `Dict[str, int]` ({"workout\_exercise\_id": new\_id})
    * Example Request:

        ```json
        {
          "exercise_id": 1,
          "order_index": 1,
          "notes": "Warm-up",
          "sets": [
            {
              "set_number": 1,
              "reps": 12,
              "weight": 135.0,
              "completed": true
            },
            {
              "set_number": 2,
              "reps": 10,
              "weight": 155.0,
              "completed": true
            }
          ]
        }
        ```

    * Example Response:

        ```json
        {
          "workout_exercise_id": 4
        }
        ```

* **`DELETE /workout-exercises/{workout_exercise_id}`**

    * Removes an exercise from a workout. This also deletes all sets associated with that workout-exercise link.
    * Path Parameters:
        * `workout_exercise_id` (int): The ID of the workout-exercise link to delete.
    * Response Model: `Dict[str, str]` ({"message": "Exercise removed from workout successfully"})
    * Raises: `HTTPException` (status\_code=404) if the workout-exercise link is not found.

* **`POST /workout-exercises/{workout_exercise_id}/sets`**

    * Adds a set to a specific workout exercise.
    * Path Parameters:
        * `workout_exercise_id` (int): The ID of the workout-exercise link.
    * Request Body: `SetCreate`
    * Response Model: `Dict[str, Any]` (includes the new set's ID)
    * Example Request:

        ```json
        {
          "set_number": 3,
          "reps": 8,
          "weight": 175.0,
          "completed": true
        }
        ```

    * Example Response:

        ```json
        {
          "set_id": 7
        }
        ```

* **`PUT /sets/{set_id}`**

    * Updates a specific set.
    * Path Parameters:
        * `set_id` (int): The ID of the set to update.
    * Request Body: `SetBase`
    * Response Model: `Dict[str, str]` ({"message": "Set updated successfully"})
    * Raises: `HTTPException` (status\_code=404) if the set is not found.
    * Example Request:

        ```json
        {
          "set_number": 3,
          "reps": 10,
          "weight": 175.0,
          "completed": true
        }
        ```

* **`DELETE /sets/{set_id}`**

    * Deletes a specific set.
    * Path Parameters:
        * `set_id` (int): The ID of the set to delete.
    * Response Model: `Dict[str, str]` ({"message": "Set deleted successfully"})
    * Raises: `HTTPException` (status\_code=404) if the set is not found.

## Pydantic Models

The API uses Pydantic models for data validation and serialization, ensuring data consistency and type safety.

* `WorkoutBase`: Base model for workout data (`workout_date`, `workout_name`, `notes`).
* `WorkoutCreate`: Model for creating a workout (inherits from `WorkoutBase`).
* `Workout`: Model for a workout with ID and timestamps (inherits from `WorkoutBase`).
* `ExerciseBase`: Base model for exercise data (`exercise_name`, `exercise_category`).
* `ExerciseCreate`: Model for creating an exercise (inherits from `ExerciseBase`).
* `Exercise`: Model for an exercise with ID (inherits from `ExerciseBase`).
* `SetBase`: Base model for set data (`set_number`, `reps`, `weight`, `duration`, `distance`, `completed`, `notes`).
* `SetCreate`: Model for creating a set (inherits from `SetBase`).
* `Set`: Model for a set with ID (inherits from `SetBase`).
* `WorkoutExerciseCreate`: Model for linking an exercise to a workout, including sets.
* `WorkoutDetail`: Model for detailed workout information, including a list of exercises and their sets.

## Database Schema

The database schema is defined in `DB.py` and consists of the following tables:

* **`workouts`**: Stores workout information (`workout_id`, `workout_date`, `workout_name`, `notes`, `created_at`).
* **`exercises`**: Stores exercise information (`exercise_id`, `exercise_name`, `exercise_category`).
* **`workout_exercises`**: Links workouts and exercises, and stores ordering/notes (`workout_exercise_id`, `workout_id`, `exercise_id`, `order_index`, `notes`).
* **`exercise_sets`**: Stores set information for each exercise (`set_id`, `workout_exercise_id`, `set_number`, `reps`, `weight`, `duration`, `distance`, `completed`, `notes`).

## Frontend

### Overview

The frontend is a PyQt5 desktop application that provides a graphical user interface for interacting with the Workout Tracker API. It offers features for adding workouts, viewing workout history, and managing exercises. The frontend uses the `api_client.py` to communicate with the backend API.

### Key Widgets and Pages

* **`main_window.py`**:  This is the main application window. It sets up the overall layout, including a title bar with navigation buttons and a stacked widget to switch between different views.  It initializes `AddWorkoutWidget`.
* **`add_workout_widget.py`**: This widget allows users to create new workouts. It includes functionality to:
    * Select a workout date and name.
    * Add exercises to the workout using the `ExerciseSelectionDialog`.
    * Record sets for each exercise, including weight, reps, duration, and distance.
    * Save the workout to the database via the API.
* **`ExercisesPage.py`**:  This page displays a table of all available exercises fetched from the API. It allows users to view exercise details like name and category.
* **`history_widget.py`**: This widget displays the user's workout history. It includes:
    * A calendar view to select workout dates.
    * A table to display workout summaries.
    * Detailed workout views showing exercises and sets.
    * Progress charts (using `matplotlib`) to visualize workout data.

### Running the Frontend

1.  Ensure the backend API is running.
2.  Execute the main script:

    ```bash
    python main.py  # or python main_window.py
    ```

### Frontend Dependencies

* **PyQt5**: For creating the graphical user interface.
* **requests**: For making HTTP requests to the backend API.
* **matplotlib**: For generating workout progress charts in the history widget.

## API Client

The `api_client.py` module encapsulates the logic for interacting with the Workout Tracker API. It provides a set of functions that map to the API endpoints, making it easier for the frontend to communicate with the backend.

**Example Usage:**

```python
from api_client import WorkoutApiClient

api_client = WorkoutApiClient()

# Get all workouts
workouts = api_client.get_workouts()
print(workouts)

# Create a new workout
new_workout = api_client.create_workout(
    workout_date="2024-07-28",
    workout
