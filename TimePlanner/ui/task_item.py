from PySide6.QtCore import QMimeData, QPoint, Qt
from PySide6.QtGui import QColor, QDrag, QFont, QPixmap
from PySide6.QtWidgets import QApplication, QCheckBox, QHBoxLayout, QLabel, QMessageBox, QSizePolicy, QWidget, QMenu


TASK_MIME_TYPE = "application/x-timeplanner-task-id"


class TaskItem(QWidget):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.drag_start_position = QPoint()
        self.setObjectName("taskCard")

        self.setFixedHeight(70)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.OpenHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(10)

        self.check_box = QCheckBox()
        self.check_box.setObjectName("taskCheckBox")
        self.check_box.setChecked(self.task.completed)
        self.check_box.stateChanged.connect(self.on_checked_changed)
        layout.addWidget(self.check_box)

        self.name_label = QLabel(self.task.name)
        self.name_label.setFont(QFont("Arial", 11))
        layout.addWidget(self.name_label, 1)

        self.duration_label = QLabel(self.duration_text)
        self.duration_label.setObjectName("durationBadge")
        self.duration_label.setAlignment(Qt.AlignCenter)
        self.duration_label.setMinimumWidth(56)
        layout.addWidget(self.duration_label)

        self.setStyleSheet(
            f"""
            #taskCard {{
                background: {QColor(self.task.color).name()};
                border-radius: 8px;
                border: 1px solid rgba(0, 0, 0, 28);
            }}
            #taskCard QLabel {{
                color: #1f2933;
                background: transparent;
            }}
            #durationBadge {{
                background: rgba(255, 255, 255, 190);
                border: 1px solid rgba(0, 0, 0, 28);
                border-radius: 9px;
                padding: 3px 7px;
                font-weight: 700;
            }}
            #taskCheckBox {{
                background: transparent;
            }}
            #taskCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid rgba(31, 41, 51, 180);
                background: rgba(255, 255, 255, 220);
            }}
            #taskCheckBox::indicator:checked {{
                background: #1F5F8B;
                border: 2px solid #1F5F8B;
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

    def on_checked_changed(self, _state=None):
        # 체크박스는 완료 상태만 표시 (타임라인에 추가하지 않음)
        self.task.completed = self.check_box.isChecked()
        window = self.window()
        if hasattr(window, "save_data"):
            window.save_data()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not event.buttons() & Qt.LeftButton:
            return

        distance = (event.position().toPoint() - self.drag_start_position).manhattanLength()
        if distance < QApplication.startDragDistance():
            return

        mime_data = QMimeData()
        mime_data.setData(TASK_MIME_TYPE, str(self.task.id).encode("utf-8"))

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())
        drag.exec(Qt.CopyAction)
        self.setCursor(Qt.OpenHandCursor)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        time_action = menu.addAction("Set Time")
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")

        chosen = menu.exec(event.globalPos())
        if chosen == time_action:
            self.on_time_clicked()
        elif chosen == edit_action:
            self.on_edit_clicked()
        elif chosen == delete_action:
            self.on_delete_clicked()

    def on_time_clicked(self):
        from ui.dialogs.duration_dialog import DurationDialog

        dialog = DurationDialog(self)
        dialog.set_duration(self.task.duration)
        if dialog.exec() == DurationDialog.Accepted:
            window = self.window()
            if hasattr(window, "set_task_duration"):
                window.set_task_duration(self.task, dialog.duration_minutes)

    def on_edit_clicked(self):
        from ui.dialogs.task_dialog import TaskDialog

        dialog = TaskDialog(self)
        dialog.set_task_name(self.task.name)
        if dialog.exec() != TaskDialog.Accepted:
            return

        self.task.name = dialog.task_name
        self.name_label.setText(self.task.name)
        window = self.window()
        if hasattr(window, "save_data"):
            window.save_data()

    def on_delete_clicked(self):
        reply = QMessageBox.question(
            self,
            "Delete Task",
            f"Are you sure you want to delete '{self.task.name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        window = self.window()
        if hasattr(window, "delete_task"):
            window.delete_task(self.task.id)
