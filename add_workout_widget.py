from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QDateEdit, QTextEdit, QDialog, QListWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QComboBox, QCheckBox, QFrame, QScrollArea,
    QSpinBox, QDoubleSpinBox, QListWidgetItem
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import json
import requests

# API client for server communication
from api_client import api_client


class ExerciseSelectionDialog(QDialog):
    """Dialog for selecting exercises to add to a workout"""
    
    exercise_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Exercise")
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self._filter_exercises)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Exercise list
        self.exercise_list = QListWidget()
        self.exercise_list.itemDoubleClicked.connect(self._on_exercise_selected)
        layout.addWidget(self.exercise_list)
        
        # Category filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        filter_layout.addWidget(self.category_combo)
        layout.addLayout(filter_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Exercise")
        self.add_button.clicked.connect(self._on_add_clicked)
        button_layout.addWidget(self.add_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Load exercises
        self.exercises = []
        self._load_exercises()
        
        # Connect category filter
        self.category_combo.currentTextChanged.connect(self._filter_exercises)
    
    def _load_exercises(self):
        """Load exercises from API"""
        try:
            self.exercises = api_client.get_exercises()
            
            # Populate category filter
            categories = set()
            for exercise in self.exercises:
                if exercise.get("exercise_category"):
                    categories.add(exercise["exercise_category"])
            
            for category in sorted(categories):
                self.category_combo.addItem(category)
            
            # Populate exercise list
            self._populate_exercise_list(self.exercises)
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error Loading Exercises",
                f"Failed to load exercises: {str(e)}"
            )
    
    def _populate_exercise_list(self, exercises):
        """Populate the exercise list with the given exercises"""
        self.exercise_list.clear()
        
        for exercise in exercises:
            item = QListWidgetItem(exercise.get("exercise_name", "Unknown"))
            item.setData(Qt.UserRole, exercise)
            self.exercise_list.addItem(item)
    
    def _filter_exercises(self):
        """Filter exercises based on search text and category"""
        search_text = self.search_input.text().lower()
        selected_category = self.category_combo.currentText()
        
        filtered_exercises = []
        for exercise in self.exercises:
            name = exercise.get("exercise_name", "").lower()
            category = exercise.get("exercise_category", "")
            
            # Check if matches search text
            if search_text and search_text not in name:
                continue
                
            # Check if matches category filter
            if selected_category != "All Categories" and category != selected_category:
                continue
                
            filtered_exercises.append(exercise)
        
        self._populate_exercise_list(filtered_exercises)
    
    def _on_exercise_selected(self, item):
        """Handle exercise selection via double-click"""
        exercise_data = item.data(Qt.UserRole)
        self.exercise_selected.emit(exercise_data)
        self.accept()
    
    def _on_add_clicked(self):
        """Handle add button click"""
        selected_items = self.exercise_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select an exercise to add."
            )
            return
            
        exercise_data = selected_items[0].data(Qt.UserRole)
        self.exercise_selected.emit(exercise_data)
        self.accept()


class SetEditor(QWidget):
    """Widget for editing a single exercise set"""
    
    delete_set = pyqtSignal(int)  # Signal when set deletion is requested
    
    def __init__(self, set_number, parent=None):
        super().__init__(parent)
        self.set_number = set_number
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Set number label
        self.set_label = QLabel(f"Set {self.set_number}")
        self.set_label.setMinimumWidth(50)
        layout.addWidget(self.set_label)
        
        # Weight input
        weight_layout = QHBoxLayout()
        weight_layout.addWidget(QLabel("Weight:"))
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setMinimum(0)
        self.weight_input.setMaximum(999.9)
        self.weight_input.setSingleStep(2.5)
        self.weight_input.setSuffix(" kg")
        weight_layout.addWidget(self.weight_input)
        layout.addLayout(weight_layout)
        
        # Reps input
        reps_layout = QHBoxLayout()
        reps_layout.addWidget(QLabel("Reps:"))
        self.reps_input = QSpinBox()
        self.reps_input.setMinimum(0)
        self.reps_input.setMaximum(999)
        reps_layout.addWidget(self.reps_input)
        layout.addLayout(reps_layout)
        
        # Duration input
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration:"))
        self.duration_input = QSpinBox()
        self.duration_input.setMinimum(0)
        self.duration_input.setMaximum(9999)
        self.duration_input.setSuffix(" sec")
        duration_layout.addWidget(self.duration_input)
        layout.addLayout(duration_layout)
        
        # Distance input
        distance_layout = QHBoxLayout()
        distance_layout.addWidget(QLabel("Distance:"))
        self.distance_input = QDoubleSpinBox()
        self.distance_input.setMinimum(0)
        self.distance_input.setMaximum(9999.9)
        self.distance_input.setSuffix(" m")
        distance_layout.addWidget(self.distance_input)
        layout.addLayout(distance_layout)
        
        # Completed checkbox
        self.completed_checkbox = QCheckBox("Completed")
        self.completed_checkbox.setChecked(True)
        layout.addWidget(self.completed_checkbox)
        
        # Notes button and popup
        self.notes_button = QPushButton("Notes")
        self.notes_button.setMaximumWidth(70)
        self.notes_button.clicked.connect(self._edit_notes)
        layout.addWidget(self.notes_button)
        
        # Notes storage
        self.notes = ""
        
        # Delete button
        self.delete_button = QPushButton("Delete")
        self.delete_button.setMaximumWidth(70)
        self.delete_button.clicked.connect(self._delete_clicked)
        layout.addWidget(self.delete_button)
    
    def _edit_notes(self):
        """Open a dialog to edit notes"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Set {self.set_number} Notes")
        dialog.setMinimumWidth(300)
        dialog.setMinimumHeight(200)
        
        layout = QVBoxLayout(dialog)
        
        notes_edit = QTextEdit()
        notes_edit.setPlainText(self.notes)
        layout.addWidget(notes_edit)
        
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(dialog.accept)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.notes = notes_edit.toPlainText()
            
            # Update button appearance if notes exist
            font = self.notes_button.font()
            font.setBold(bool(self.notes))
            self.notes_button.setFont(font)
    
    def _delete_clicked(self):
        """Handle delete button click"""
        self.delete_set.emit(self.set_number)
    
    def get_set_data(self):
        """Get the set data as a dictionary"""
        return {
            "set_number": self.set_number,
            "weight": self.weight_input.value() if self.weight_input.value() > 0 else None,
            "reps": self.reps_input.value() if self.reps_input.value() > 0 else None,
            "duration": self.duration_input.value() if self.duration_input.value() > 0 else None,
            "distance": self.distance_input.value() if self.distance_input.value() > 0 else None,
            "completed": self.completed_checkbox.isChecked(),
            "notes": self.notes if self.notes else None
        }
    
    def set_data(self, data):
        """Set the widget values from a data dictionary"""
        if "weight" in data and data["weight"] is not None:
            self.weight_input.setValue(data["weight"])
        
        if "reps" in data and data["reps"] is not None:
            self.reps_input.setValue(data["reps"])
        
        if "duration" in data and data["duration"] is not None:
            self.duration_input.setValue(data["duration"])
        
        if "distance" in data and data["distance"] is not None:
            self.distance_input.setValue(data["distance"])
        
        if "completed" in data:
            self.completed_checkbox.setChecked(data["completed"])
        
        if "notes" in data and data["notes"]:
            self.notes = data["notes"]
            font = self.notes_button.font()
            font.setBold(True)
            self.notes_button.setFont(font)


class ExerciseWidget(QWidget):
    """Widget for displaying and editing an exercise in a workout"""
    
    delete_exercise = pyqtSignal(int)  # Signal when exercise deletion is requested
    move_up = pyqtSignal(int)  # Signal to move exercise up
    move_down = pyqtSignal(int)  # Signal to move exercise down
    
    def __init__(self, exercise_data, order_index, parent=None):
        super().__init__(parent)
        self.exercise_data = exercise_data
        self.order_index = order_index
        self.set_editors = []
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Frame for the exercise
        exercise_frame = QFrame()
        exercise_frame.setFrameShape(QFrame.StyledPanel)
        exercise_frame.setFrameShadow(QFrame.Raised)
        frame_layout = QVBoxLayout(exercise_frame)
        
        # Exercise header
        header_layout = QHBoxLayout()
        
        # Exercise name
        self.name_label = QLabel(self.exercise_data.get("exercise_name", "Unknown Exercise"))
        font = self.name_label.font()
        font.setBold(True)
        font.setPointSize(12)
        self.name_label.setFont(font)
        header_layout.addWidget(self.name_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Order index controls
        self.up_button = QPushButton("▲")
        self.up_button.setMaximumWidth(30)
        self.up_button.clicked.connect(lambda: self.move_up.emit(self.order_index))
        header_layout.addWidget(self.up_button)
        
        self.down_button = QPushButton("▼")
        self.down_button.setMaximumWidth(30)
        self.down_button.clicked.connect(lambda: self.move_down.emit(self.order_index))
        header_layout.addWidget(self.down_button)
        
        # Notes button
        self.notes_button = QPushButton("Notes")
        self.notes_button.setMaximumWidth(70)
        self.notes_button.clicked.connect(self._edit_notes)
        header_layout.addWidget(self.notes_button)
        
        # Delete button
        self.delete_button = QPushButton("Delete")
        self.delete_button.setMaximumWidth(70)
        self.delete_button.clicked.connect(self._delete_clicked)
        header_layout.addWidget(self.delete_button)
        
        frame_layout.addLayout(header_layout)
        
        # Sets container
        self.sets_container = QWidget()
        self.sets_layout = QVBoxLayout(self.sets_container)
        self.sets_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(self.sets_container)
        
        # Add set button
        self.add_set_button = QPushButton("Add Set")
        self.add_set_button.clicked.connect(self._add_set)
        frame_layout.addWidget(self.add_set_button)
        
        main_layout.addWidget(exercise_frame)
        
        # Add an initial set
        self._add_set()
        
        # Exercise notes storage
        self.notes = ""
    
    def _add_set(self):
        """Add a new set to the exercise"""
        set_number = len(self.set_editors) + 1
        set_editor = SetEditor(set_number)
        set_editor.delete_set.connect(self._delete_set)
        
        self.sets_layout.addWidget(set_editor)
        self.set_editors.append(set_editor)
    
    def _delete_set(self, set_number):
        """Delete a set and renumber the remaining sets"""
        # Find the set editor to remove
        index_to_remove = set_number - 1
        if 0 <= index_to_remove < len(self.set_editors):
            # Remove from layout and list
            set_editor = self.set_editors.pop(index_to_remove)
            set_editor.setParent(None)
            set_editor.deleteLater()
            
            # Renumber remaining sets
            for i, editor in enumerate(self.set_editors):
                editor.set_number = i + 1
                editor.set_label.setText(f"Set {i + 1}")
    
    def _edit_notes(self):
        """Open a dialog to edit exercise notes"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Exercise Notes")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(200)
        
        layout = QVBoxLayout(dialog)
        
        notes_edit = QTextEdit()
        notes_edit.setPlainText(self.notes)
        layout.addWidget(notes_edit)
        
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(dialog.accept)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.notes = notes_edit.toPlainText()
            
            # Update button appearance if notes exist
            font = self.notes_button.font()
            font.setBold(bool(self.notes))
            self.notes_button.setFont(font)
    
    def _delete_clicked(self):
        """Handle delete button click"""
        self.delete_exercise.emit(self.order_index)
    
    def get_exercise_data(self):
        """Get the exercise data as a dictionary"""
        sets_data = []
        for set_editor in self.set_editors:
            sets_data.append(set_editor.get_set_data())
        
        return {
            "exercise_id": self.exercise_data.get("exercise_id"),
            "exercise_name": self.exercise_data.get("exercise_name"),
            "order_index": self.order_index,
            "notes": self.notes if self.notes else None,
            "sets": sets_data
        }
    
    def update_order_index(self, new_index):
        """Update the order index of this exercise"""
        self.order_index = new_index


class AddWorkoutWidget(QWidget):
    """Widget for adding a new workout with exercises and sets"""
    
    workout_saved = pyqtSignal(int)  # Signal when workout is saved successfully
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exercise_widgets = []
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Workout metadata section
        metadata_group = QFrame()
        metadata_group.setFrameShape(QFrame.StyledPanel)
        metadata_layout = QVBoxLayout(metadata_group)
        
        # Title
        title_label = QLabel("Add New Workout")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        metadata_layout.addWidget(title_label)
        
        # Date and name
        form_layout = QHBoxLayout()
        
        # Date picker
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_picker)
        form_layout.addLayout(date_layout)
        
        # Workout name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Workout Name:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)
        
        metadata_layout.addLayout(form_layout)
        
        # Notes
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("Notes:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        notes_layout.addWidget(self.notes_input)
        metadata_layout.addLayout(notes_layout)
        
        main_layout.addWidget(metadata_group)
        
        # Exercise section
        exercise_group = QFrame()
        exercise_group.setFrameShape(QFrame.StyledPanel)
        exercise_layout = QVBoxLayout(exercise_group)
        
        # Exercise list header
        exercise_header = QHBoxLayout()
        exercise_header.addWidget(QLabel("Exercises"))
        exercise_header.addStretch()
        
        # Add exercise button
        self.add_exercise_button = QPushButton("Add Exercise")
        self.add_exercise_button.clicked.connect(self._open_exercise_selection)
        exercise_header.addWidget(self.add_exercise_button)
        
        exercise_layout.addLayout(exercise_header)
        
        # Scroll area for exercises
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Container for exercise widgets
        self.exercises_container = QWidget()
        self.exercises_layout = QVBoxLayout(self.exercises_container)
        self.exercises_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(self.exercises_container)
        exercise_layout.addWidget(scroll_area)
        
        main_layout.addWidget(exercise_group)
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.clear_button = QPushButton("Clear Form")
        self.clear_button.clicked.connect(self._clear_form)
        buttons_layout.addWidget(self.clear_button)
        
        self.save_button = QPushButton("Save Workout")
        self.save_button.clicked.connect(self._save_workout)
        buttons_layout.addWidget(self.save_button)
        
        main_layout.addLayout(buttons_layout)
    
    def _open_exercise_selection(self):
        """Open the exercise selection dialog"""
        dialog = ExerciseSelectionDialog(self)
        dialog.exercise_selected.connect(self._add_exercise)
        dialog.exec_()
    
    def _add_exercise(self, exercise_data):
        """Add a new exercise to the workout"""
        order_index = len(self.exercise_widgets)
        exercise_widget = ExerciseWidget(exercise_data, order_index)
        
        # Connect signals
        exercise_widget.delete_exercise.connect(self._delete_exercise)
        exercise_widget.move_up.connect(self._move_exercise_up)
        exercise_widget.move_down.connect(self._move_exercise_down)
        
        self.exercises_layout.addWidget(exercise_widget)
        self.exercise_widgets.append(exercise_widget)
    
    def _delete_exercise(self, index):
        """Delete an exercise and update the order indexes"""
        if 0 <= index < len(self.exercise_widgets):
            # Remove from layout and list
            widget = self.exercise_widgets.pop(index)
            widget.setParent(None)
            widget.deleteLater()
            
            # Update order indexes for remaining exercises
            for i, widget in enumerate(self.exercise_widgets):
                widget.update_order_index(i)
    
    def _move_exercise_up(self, index):
        """Move an exercise up in the order"""
        if index > 0:
            # Swap widgets in the list
            self.exercise_widgets[index], self.exercise_widgets[index-1] = \
                self.exercise_widgets[index-1], self.exercise_widgets[index]
            
            # Update order indexes
            self.exercise_widgets[index].update_order_index(index)
            self.exercise_widgets[index-1].update_order_index(index-1)
            
            # Rebuild the layout
            self._rebuild_exercises_layout()
    
    def _move_exercise_down(self, index):
        """Move an exercise down in the order"""
        if index < len(self.exercise_widgets) - 1:
            # Swap widgets in the list
            self.exercise_widgets[index], self.exercise_widgets[index+1] = \
                self.exercise_widgets[index+1], self.exercise_widgets[index]
            
            # Update order indexes
            self.exercise_widgets[index].update_order_index(index)
            self.exercise_widgets[index+1].update_order_index(index+1)
            
            # Rebuild the layout
            self._rebuild_exercises_layout()
    
    def _rebuild_exercises_layout(self):
        """Rebuild the exercises layout with the current order"""
        # Remove all widgets from layout
        while self.exercises_layout.count():
            item = self.exercises_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Add widgets back in the new order
        for widget in self.exercise_widgets:
            self.exercises_layout.addWidget(widget)
    
    def _clear_form(self):
        """Clear all form inputs"""
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to clear all workout data?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset inputs
            self.date_picker.setDate(QDate.currentDate())
            self.name_input.clear()
            self.notes_input.clear()
            
            # Remove all exercises
            for widget in self.exercise_widgets:
                widget.setParent(None)
                widget.deleteLater()
            
            self.exercise_widgets = []
    
    def _save_workout(self):
        """Save the workout to the API"""
        # Validate inputs
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please enter a workout name."
            )
            return
        
        if not self.exercise_widgets:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please add at least one exercise to the workout."
            )
            return
        
        # Prepare workout data
        workout_date = self.date_picker.date().toString("yyyy-MM-dd")
        workout_name = self.name_input.text().strip()
        notes = self.notes_input.toPlainText().strip() or None
        
        # First create the workout
        try:
            workout_data = {
                "workout_date": workout_date,
                "workout_name": workout_name,
                "notes": notes
            }
            
            # Create workout
            response = api_client.create_workout(workout_data)
            workout_id = response.get("workout_id")
            
            if not workout_id:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to create workout. No workout ID returned."
                )
                return
            
            # Add exercises to workout
            for i, widget in enumerate(self.exercise_widgets):
                exercise_data = widget.get_exercise_data()
                
                # Prepare exercise data for API
                exercise_payload = {
                    "exercise_id": exercise_data["exercise_id"],
                    "order_index": i,
                    "notes": exercise_data["notes"],
                    "sets": exercise_data["sets"]
                }
                
                # Add exercise to workout
                api_client.add_exercise_to_workout(workout_id, exercise_payload)
            
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Workout #{workout_id} saved successfully!"
            )
            
            # Clear form
            self._clear_form()
            
            # Emit signal
            self.workout_saved.emit(workout_id)
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to save workout: {str(e)}"
            )