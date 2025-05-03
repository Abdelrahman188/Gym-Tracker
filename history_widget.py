from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCalendarWidget,
    QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QPushButton, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import matplotlib
matplotlib.use('Qt5Agg', force=True)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from api_client import api_client
from datetime import datetime
from typing import List, Dict


class WorkoutCalendar(QCalendarWidget):
    """Custom calendar widget that highlights days with workouts."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.workout_dates = set()  # Set of dates with workouts
        
        # Configure calendar
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setSelectionMode(QCalendarWidget.SingleSelection)
        
    def set_workout_dates(self, dates):
        """Set the dates that have workouts to highlight them."""
        self.workout_dates = set(dates)
        self.updateCells()
        
    def paintCell(self, painter, rect, date):
        """Override paintCell to highlight days with workouts."""
        super().paintCell(painter, rect, date)
        
        if date.toPyDate() in self.workout_dates:
            # Draw highlight for workout dates
            painter.save()
            painter.setBrush(QColor(0, 128, 255, 60))  # Semi-transparent blue
            painter.setPen(Qt.NoPen)
            painter.drawRect(rect)
            painter.restore()


class ProgressChart(FigureCanvas):
    """Widget for displaying workout progress charts."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """Initialize the progress chart."""
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        # Set some matplotlib defaults
        matplotlib.rcParams['font.size'] = 9
        self.fig.tight_layout()
        
    def plot_exercise_progress(self, exercise_name, data):
        """Plot progress for a specific exercise over time."""
        # Clear previous plots
        self.axes.clear()
        
        if not data:
            self.axes.set_title("No data available")
            self.draw()
            return
            
        # Extract dates and weight/reps values
        dates = [item['date'] for item in data]
        weights = [item['weight'] for item in data]
        reps = [item['reps'] for item in data]
        
        # Convert dates to datetime objects if they're strings
        if isinstance(dates[0], str):
            dates = [datetime.strptime(d, '%Y-%m-%d').date() for d in dates]
        
        # Plot weight values
        color1 = '#3366cc'  # Blue
        self.axes.plot(dates, weights, 'o-', color=color1, label='Weight (kg)')
        self.axes.set_ylabel('Weight (kg)', color=color1)
        self.axes.tick_params(axis='y', labelcolor=color1)
        
        # Create a twin axes for reps
        ax2 = self.axes.twinx()
        color2 = '#cc3366'  # Red
        ax2.plot(dates, reps, 's-', color=color2, label='Reps')
        ax2.set_ylabel('Reps', color=color2)
        ax2.tick_params(axis='y', labelcolor=color2)
        
        # Set title and format x-axis
        self.axes.set_title(f"Progress for {exercise_name}")
        self.axes.set_xlabel("Date")
        
        # Add legend
        lines1, labels1 = self.axes.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.axes.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Format dates on x-axis
        self.fig.autofmt_xdate()
        
        self.fig.tight_layout()
        self.draw()


class WorkoutDetailWidget(QScrollArea):
    """Widget to display details of a selected workout."""
    
    delete_requested = pyqtSignal(int)  # Signal when workout deletion is requested
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        
        # Create container for scroll area
        self.content_widget = QWidget()
        self.setWidget(self.content_widget)
        
        # Main layout
        self.layout = QVBoxLayout(self.content_widget)
        self.layout.setAlignment(Qt.AlignTop)
        
        # Title and info will be added dynamically
        self.title_label = QLabel()
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.layout.addWidget(self.title_label)
        
        self.date_label = QLabel()
        date_font = QFont()
        date_font.setPointSize(10)
        date_font.setItalic(True)
        self.date_label.setFont(date_font)
        self.layout.addWidget(self.date_label)
        
        self.notes_label = QLabel()
        self.notes_label.setWordWrap(True)
        self.layout.addWidget(self.notes_label)
        
        # Separator
        self._add_separator()
        
        # Container for exercise details
        self.exercises_container = QWidget()
        self.exercises_layout = QVBoxLayout(self.exercises_container)
        self.layout.addWidget(self.exercises_container)
        
        # Add delete button
        self.delete_btn = QPushButton("Delete Workout")
        self.delete_btn.setMaximumWidth(150)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        self.layout.addWidget(self.delete_btn)
        
        # Store the current workout ID
        self.current_workout_id = None
        
    def _add_separator(self):
        """Add a horizontal separator line."""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)
        
    def _on_delete_clicked(self):
        """Handle delete button click."""
        if self.current_workout_id is not None:
            # Confirm deletion
            reply = QMessageBox.question(
                self, 
                "Confirm Deletion", 
                "Are you sure you want to delete this workout?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.delete_requested.emit