from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCalendarWidget,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from core.models import Block
from core.scheduler import Scheduler
from core.storage import Storage
from ui.left_panel import LeftPanel
from ui.timetable import TimeTable


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("mainWindow")
        self.setWindowTitle("Time Planner")
        self.resize(1400, 760)

        self.data = self.load_data()
        self.left_panel = LeftPanel(self)

        self.top_date_label = QLabel(self.data.get("date", date.today().isoformat()))
        self.top_date_label.setObjectName("dateLabel")
        self.top_date_label.setAlignment(Qt.AlignCenter)
        self.top_date_label.setCursor(Qt.PointingHandCursor)
        self.top_date_label.mousePressEvent = self.on_date_label_clicked

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        left_layout.addWidget(self.top_date_label)
        left_layout.addWidget(self.left_panel)

        timetable_container = QWidget()
        timetable_container.setObjectName("timetableContainer")
        timetable_layout = QHBoxLayout(timetable_container)
        timetable_layout.setContentsMargins(12, 12, 12, 12)
        timetable_layout.setSpacing(14)

        self.timetable1 = TimeTable(self, title="Morning 00:00-11:59")
        self.timetable2 = TimeTable(self, title="Afternoon 12:00-23:59")
        timetable_layout.addWidget(self.timetable1)
        timetable_layout.addWidget(self.timetable2)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        main_layout.addWidget(left_container, 2)
        main_layout.addWidget(timetable_container, 5)
        self.setCentralWidget(main_widget)

        self.apply_styles()
        self.refresh_timetables()

    def load_data(self):
        loaded = Storage.load()
        if loaded is None:
            return {"date": date.today().isoformat(), "tasks": [], "blocks": []}
        return loaded

    def save_data(self):
        Storage.save(self.data["date"], self.data["tasks"], self.data["blocks"])

    def set_task_duration(self, task, duration):
        task.duration = duration

        block = self.find_block(task.id)
        if block is not None:
            if duration <= 0:
                self.data["blocks"].remove(block)
                task.completed = False
            else:
                old_start = block.start
                new_length = self.duration_to_cells(duration)
                self.data["blocks"].remove(block)

                if Scheduler.can_place(self.data["blocks"], old_start, new_length):
                    self.data["blocks"].append(Block(task_id=task.id, start=old_start, length=new_length))
                else:
                    new_start = Scheduler.find_first_available_start(self.data["blocks"], new_length)
                    if new_start is None:
                        task.completed = False
                    else:
                        self.data["blocks"].append(Block(task_id=task.id, start=new_start, length=new_length))

        self.save_data()
        self.refresh_timetables()
        self.left_panel.sync_task_items()

    def set_task_completed(self, task, completed):
        block = self.find_block(task.id)

        if completed:
            if task.duration <= 0:
                task.completed = False
                self.save_data()
                return

            if block is None:
                length = self.duration_to_cells(task.duration)
                start = Scheduler.find_first_available_start(self.data["blocks"], length)
                if start is None:
                    task.completed = False
                    self.save_data()
                    return
                self.data["blocks"].append(Block(task_id=task.id, start=start, length=length))

            task.completed = True
        else:
            if block is not None:
                self.data["blocks"].remove(block)
            task.completed = False

        self.save_data()
        self.refresh_timetables()

    def place_task_at(self, task_id, start):
        task = self.find_task(task_id)
        if task is None:
            return False

        if task.duration <= 0:
            from ui.dialogs.duration_dialog import DurationDialog

            dialog = DurationDialog(self)
            if dialog.exec() != DurationDialog.Accepted or dialog.duration_minutes <= 0:
                return False
            task.duration = dialog.duration_minutes

        length = self.duration_to_cells(task.duration)
        if start + length > 24 * 6:
            return False

        current_block = self.find_block(task_id)
        if current_block is not None:
            self.data["blocks"].remove(current_block)

        if not Scheduler.can_place(self.data["blocks"], start, length):
            if current_block is not None:
                self.data["blocks"].append(current_block)
            return False

        self.data["blocks"].append(Block(task_id=task_id, start=start, length=length))
        task.completed = True
        self.save_data()
        self.refresh_timetables()
        self.left_panel.sync_task_items()
        return True

    def find_task(self, task_id):
        return next((task for task in self.data["tasks"] if task.id == task_id), None)

    def find_block(self, task_id):
        return next((block for block in self.data["blocks"] if block.task_id == task_id), None)

    def duration_to_cells(self, duration):
        return max(1, (duration + 9) // 10)

    def refresh_timetables(self):
        self.timetable1.canvas.set_data(self.data["tasks"], self.data["blocks"], 0)
        self.timetable2.canvas.set_data(self.data["tasks"], self.data["blocks"], 72)

    def on_date_label_clicked(self, event):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Date")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        calendar = QCalendarWidget()
        selected_date = date.fromisoformat(self.data["date"])
        calendar.setSelectedDate(QDate(selected_date.year, selected_date.month, selected_date.day))
        layout.addWidget(calendar)

        def on_date_selected():
            selected_qdate = calendar.selectedDate()
            self.data["date"] = selected_qdate.toPython().isoformat()
            self.top_date_label.setText(self.data["date"])
            self.save_data()
            self.refresh_timetables()
            dialog.accept()

        calendar.clicked.connect(on_date_selected)
        dialog.exec()

    def apply_styles(self):
        self.setStyleSheet(
            """
            #mainWindow, QWidget {
                background: #F2F5F8;
                color: #1F2933;
                font-family: Arial;
            }
            #dateLabel {
                background: #FFFFFF;
                border: 1px solid #D9E2EC;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 700;
                padding: 10px;
            }
            #leftPanel, #timetableContainer {
                background: #FFFFFF;
                border: 1px solid #D9E2EC;
                border-radius: 10px;
            }
            #panelTitle, #tableTitle {
                color: #334E68;
                font-size: 14px;
                font-weight: 700;
                padding: 4px;
            }
            QPushButton {
                background: #286DA8;
                color: #FFFFFF;
                border: none;
                border-radius: 7px;
                padding: 9px 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #1F5F8B;
            }
            QCheckBox {
                background: transparent;
            }
            """
        )
