
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from api_client import api_client

class ExercisesWindow(QMainWindow):
    """PyQt5 window to display all available exercises."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Available Exercises")
        self.resize(600, 400)

        # Main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Table widget setup
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category"])
        layout.addWidget(self.table)

        # Load data
        self.load_exercises()

    def load_exercises(self):
        """Fetch exercises from the API and populate the table."""
        try:
            exercises = api_client.get_exercises()
        except Exception as e:
            print(f"Error fetching exercises: {e}")
            exercises = []

        self.table.setRowCount(len(exercises))
        for row, exercise in enumerate(exercises):
            self.table.setItem(row, 0, QTableWidgetItem(str(exercise.get("exercise_id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(exercise.get("exercise_name", "")))
            category = exercise.get("exercise_category") or "—"
            self.table.setItem(row, 2, QTableWidgetItem(category))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExercisesWindow()
    window.show()
    sys.exit(app.exec_())
