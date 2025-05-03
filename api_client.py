import requests
from typing import Dict, List, Any, Optional
from datetime import date


class WorkoutApiClient:
    """Client for interacting with the Workout Tracker API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """Initialize the API client with base URL."""
        self.base_url = base_url
    
    def _handle_response(self, response: requests.Response) -> Any:
        """Process API response and handle errors."""
        response.raise_for_status()
        return response.json()
    
    # Workout endpoints
    def get_workouts(self) -> List[Dict]:
        """Get all workouts."""
        response = requests.get(f"{self.base_url}/workouts")
        return self._handle_response(response)
    
    def get_workout_details(self, workout_id: int) -> Dict:
        """Get details for a specific workout."""
        response = requests.get(f"{self.base_url}/workouts/{workout_id}")
        return self._handle_response(response)
    
    def create_workout(self, workout_date: date, workout_name: str, notes: Optional[str] = None) -> Dict:
        """Create a new workout."""
        payload = {
            "workout_date": workout_date.isoformat(),
            "workout_name": workout_name,
            "notes": notes
        }
        response = requests.post(f"{self.base_url}/workouts", json=payload)
        return self._handle_response(response)
    
    def delete_workout(self, workout_id: int) -> Dict:
        """Delete a workout."""
        response = requests.delete(f"{self.base_url}/workouts/{workout_id}")
        return self._handle_response(response)
    
    # Exercise endpoints
    def get_exercises(self) -> List[Dict]:
        """Get all exercises."""
        response = requests.get(f"{self.base_url}/exercises")
        return self._handle_response(response)
    
    def create_exercise(self, exercise_name: str, exercise_category: Optional[str] = None) -> Dict:
        """Create a new exercise."""
        payload = {
            "exercise_name": exercise_name,
            "exercise_category": exercise_category
        }
        response = requests.post(f"{self.base_url}/exercises", json=payload)
        return self._handle_response(response)
    
    # Workout-Exercise linking
    def add_exercise_to_workout(
        self, 
        workout_id: int, 
        exercise_id: int,
        order_index: int,
        sets: List[Dict],
        notes: Optional[str] = None
    ) -> Dict:
        """Add an exercise with sets to a workout."""
        payload = {
            "exercise_id": exercise_id,
            "order_index": order_index,
            "notes": notes,
            "sets": sets
        }
        response = requests.post(
            f"{self.base_url}/workouts/{workout_id}/exercises", 
            json=payload
        )
        return self._handle_response(response)
    
    def delete_workout_exercise(self, workout_exercise_id: int) -> Dict:
        """Remove an exercise from a workout."""
        response = requests.delete(f"{self.base_url}/workout-exercises/{workout_exercise_id}")
        return self._handle_response(response)
    
    # Set operations
    def add_set(self, workout_exercise_id: int, set_data: Dict) -> Dict:
        """Add a set to a workout exercise."""
        response = requests.post(
            f"{self.base_url}/workout-exercises/{workout_exercise_id}/sets",
            json=set_data
        )
        return self._handle_response(response)
    
    def update_set(self, set_id: int, set_data: Dict) -> Dict:
        """Update a set."""
        response = requests.put(f"{self.base_url}/sets/{set_id}", json=set_data)
        return self._handle_response(response)
    
    def delete_set(self, set_id: int) -> Dict:
        """Delete a set."""
        response = requests.delete(f"{self.base_url}/sets/{set_id}")
        return self._handle_response(response)


# Create a single instance to be used throughout the app
api_client = WorkoutApiClient()