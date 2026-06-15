from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QLabel, QHBoxLayout, QWidget, QSizePolicy
from PySide6.QtCore import Qt


class TaskItem(QWidget):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task

        # 블록 높이 고정
        self.setFixedHeight(70)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(10)

        self.status_label = QLabel("□")
        self.status_label.setFixedWidth(20)
        layout.addWidget(self.status_label)

        self.name_label = QLabel(self.task.name)
        self.name_label.setFont(QFont("Arial", 11))
        layout.addWidget(self.name_label)

        self.duration_label = QLabel(self.duration_text)
        layout.addWidget(self.duration_label)

        # 기존 색상 디자인 유지
        self.setStyleSheet(
            f"background: {QColor(self.task.color).name()}; border-radius: 6px;"
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
