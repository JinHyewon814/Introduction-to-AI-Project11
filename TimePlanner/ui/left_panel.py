from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtCore import Qt
from ui.task_list import TaskList
from ui.dialogs.task_dialog import TaskDialog
from core.models import Task
from core.constants import TASK_COLORS


class LeftPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        self.date_label = QLabel("Date")
        self.date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.date_label)

        self.task_list = TaskList(self)
        layout.addWidget(self.task_list, 1)

        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.on_add_task_clicked)
        layout.addWidget(self.add_task_button)
        
        # Load existing tasks
        self.load_tasks()

    def load_tasks(self):
        """Load existing tasks into the UI"""
        from ui.task_item import TaskItem
        for task_data in self.parent_window.data["tasks"]:
            if isinstance(task_data, dict):
                task = Task.from_dict(task_data)
            else:
                task = task_data
            task_item = TaskItem(task, self.task_list)
            self.task_list.add_task_item(task_item)

    def on_add_task_clicked(self):
        dialog = TaskDialog(self)
        if dialog.exec() == TaskDialog.Accepted:
            task_name = dialog.task_name
            if task_name:
                # Generate new task ID
                max_id = 0
                for task_data in self.parent_window.data["tasks"]:
                    if isinstance(task_data, dict):
                        max_id = max(max_id, task_data.get('id', 0))
                    else:
                        max_id = max(max_id, task_data.id)
                new_id = max_id + 1
                
                # Select color
                color = TASK_COLORS[new_id % len(TASK_COLORS)]
                
                # Create task
                new_task = Task(id=new_id, name=task_name, color=color)
                
                # Add to data
                self.parent_window.data["tasks"].append(new_task)
                self.parent_window.save_data()
                
                # Add to UI
                from ui.task_item import TaskItem
                task_item = TaskItem(new_task, self.task_list)
                self.task_list.add_task_item(task_item)
