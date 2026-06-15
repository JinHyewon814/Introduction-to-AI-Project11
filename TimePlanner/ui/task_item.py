from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QLabel, QHBoxLayout, QWidget, QSizePolicy
from PySide6.QtCore import Qt


class TaskItem(QWidget):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task

        # Task 블록 크기 고정
        self.setFixedHeight(70)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        self.status_label = QLabel("□")
        self.status_label.setFixedWidth(24)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.name_label = QLabel(self.task.name)
        self.name_label.setFont(QFont("Arial", 11))
        self.name_label.setAlignment(Qt.AlignVCenter)
        layout.addWidget(self.name_label, 1)

        self.duration_label = QLabel(self.duration_text)
        self.duration_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        layout.addWidget(self.duration_label)

        self.setStyleSheet(
            f"""
            TaskItem {{
                background: {QColor(self.task.color).name()};
                border-radius: 6px;
            }}
            """
        )

    @property
    def duration_text(self):
        if self.task.duration <= 0:
            return ""
        hours = self.task.duration // 60
        minutes = self.task.duration % 60
        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        return f"({' '.join(parts)})"
