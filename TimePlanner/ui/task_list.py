from PySide6.QtWidgets import QVBoxLayout, QWidget

from ui.task_item import TaskItem


class TaskList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)

    def add_task_item(self, task_item: TaskItem):
        self.layout.addWidget(task_item)
