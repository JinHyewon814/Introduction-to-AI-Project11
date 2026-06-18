from PySide6.QtWidgets import QVBoxLayout, QWidget

from ui.task_item import TaskItem


class TaskList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        # 남는 공간을 아래쪽으로 밀어내서 TaskItem들이 세로로 늘어나지 않게 함
        self.layout.addStretch()

    def add_task_item(self, task_item: TaskItem):
        # TaskItem 높이 고정
        task_item.setFixedHeight(70)

        # stretch 위쪽에 task를 추가해야 task들이 위에서부터 쌓임
        self.layout.insertWidget(self.layout.count() - 1, task_item)
