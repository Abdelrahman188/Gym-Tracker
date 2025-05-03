import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QPushButton, 
    QVBoxLayout, QStackedWidget, QApplication, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from add_workout_widget import ExerciseWidget
from add_workout_widget import AddWorkoutWidget

class MainWindow(QMainWindow):
    """Main window for the Gym Workout Assistant."""
    
    def __init__(self):
        super().__init__()
        # Configure window properties
        self.setWindowTitle("Gym Workout Assistant")
        self.setMinimumSize(800, 600)
        
        # Create and set the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create the title bar and navigation buttons
        self.create_title_bar()
        
        # Create the stacked widget for different pages
        self.pages = QStackedWidget()
        
        # Create and add the different pages
        self.add_workout_page = AddWorkoutWidget()
       
        
        
        self.pages.addWidget(self.add_workout_page)
        
        
        
        # Add stacked widget to main layout
        self.main_layout.addWidget(self.pages)
        
    def create_title_bar(self):
        """Create the title bar with app title and navigation buttons."""
        # Create title bar widget
        title_bar = QWidget()
        title_bar_layout = QHBoxLayout(title_bar)
        
        # Add app title
        title_label = QLabel("Gym Workout Assistant")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_bar_layout.addWidget(title_label)
        
        # Add spacer to push buttons to the right
        title_bar_layout.addStretch()
        
        # Create navigation buttons
        self.add_workout_btn = self.create_nav_button("Add Workout", 0)
        self.history_btn = self.create_nav_button("History", 1)
        self.exercises_btn = self.create_nav_button("Exercises List", 2)
        
        # Add buttons to title bar
        title_bar_layout.addWidget(self.add_workout_btn)
        
        # Add title bar to main layout
        self.main_layout.addWidget(title_bar)
    
    def create_nav_button(self, text, page_index):
        """Create a navigation button."""
        button = QPushButton(text)
        button.setMinimumWidth(120)
        button.setMinimumHeight(40)
        button.clicked.connect(lambda: self.pages.setCurrentIndex(page_index))
        return button


# For testing the main window independently
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())