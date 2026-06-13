from datetime import date

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QWidget, QVBoxLayout, QCalendarWidget, QDialog

from ui.left_panel import LeftPanel
from ui.timetable import TimeTable
from core.storage import Storage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Planner")
        self.resize(1400, 700)

        self.data = self.load_data()

        self.left_panel = LeftPanel(self)
        
        # Create two timetables side by side
        timetable_container = QWidget()
        timetable_layout = QHBoxLayout(timetable_container)
        timetable_layout.setContentsMargins(0, 0, 0, 0)
        timetable_layout.setSpacing(10)
        
        self.timetable1 = TimeTable(self, title="Morning (00:00-11:59)")
        self.timetable2 = TimeTable(self, title="Afternoon (12:00-23:59)")
        
        timetable_layout.addWidget(self.timetable1)
        timetable_layout.addWidget(self.timetable2)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.addWidget(self.left_panel, 2)
        main_layout.addWidget(timetable_container, 5)
        self.setCentralWidget(main_widget)

        self.top_date_label = QLabel(self.data.get("date", date.today().isoformat()))
        self.top_date_label.setAlignment(Qt.AlignCenter)
        self.top_date_label.setCursor(Qt.PointingHandCursor)
        self.top_date_label.mousePressEvent = self.on_date_label_clicked
        self.statusBar().addPermanentWidget(self.top_date_label)

    def load_data(self):
        loaded = Storage.load()
        if loaded is None:
            return {"date": date.today().isoformat(), "tasks": [], "blocks": []}
        return loaded

    def save_data(self):
        Storage.save(self.data["date"], self.data["tasks"], self.data["blocks"])
    
    def on_date_label_clicked(self, event):
        """Show calendar dialog to select date"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Date")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # Create calendar widget
        calendar = QCalendarWidget()
        selected_date = date.fromisoformat(self.data["date"])
        calendar.setSelectedDate(QDate(selected_date.year, selected_date.month, selected_date.day))
        layout.addWidget(calendar)
        
        # Connect date selection
        def on_date_selected():
            selected_qdate = calendar.selectedDate()
            self.data["date"] = selected_qdate.toPython().isoformat()
            self.top_date_label.setText(self.data["date"])
            self.save_data()
            dialog.accept()
        
        calendar.clicked.connect(on_date_selected)
        dialog.exec()
