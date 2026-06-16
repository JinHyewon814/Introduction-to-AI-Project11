from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from core.constants import TASK_COLORS
from core.models import Task
from ui.dialogs.task_dialog import TaskDialog
from ui.task_list import TaskList


class LeftPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("leftPanel")
        self.parent_window = parent

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.date_label = QLabel("Tasks")
        self.date_label.setObjectName("panelTitle")
        self.date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.date_label)

        self.task_list = TaskList(self)
        layout.addWidget(self.task_list, 1)

        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.on_add_task_clicked)
        layout.addWidget(self.add_task_button)

        self.load_tasks()

    def load_tasks(self):
        from ui.task_item import TaskItem

        for task_data in self.parent_window.data["tasks"]:
            task = Task.from_dict(task_data) if isinstance(task_data, dict) else task_data
            task_item = TaskItem(task, self.task_list)
            self.task_list.add_task_item(task_item)

    def sync_task_items(self):
        from ui.task_item import TaskItem

        for task_item in self.findChildren(TaskItem):
            task_item.duration_label.setText(task_item.duration_text)
            task_item.check_box.blockSignals(True)
            task_item.check_box.setChecked(task_item.task.completed)
            task_item.check_box.blockSignals(False)

    def on_add_task_clicked(self):
        dialog = TaskDialog(self)
        if dialog.exec() != TaskDialog.Accepted:
            return

        task_name = dialog.task_name
        if not task_name:
            return

        max_id = max((task.id for task in self.parent_window.data["tasks"]), default=0)
        new_id = max_id + 1
        color = TASK_COLORS[new_id % len(TASK_COLORS)]
        new_task = Task(id=new_id, name=task_name, color=color)

        self.parent_window.data["tasks"].append(new_task)
        self.parent_window.save_data()

        from ui.task_item import TaskItem

        task_item = TaskItem(new_task, self.task_list)
        self.task_list.add_task_item(task_item)
