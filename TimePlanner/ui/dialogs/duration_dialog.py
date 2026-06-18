from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QSpinBox, QVBoxLayout


class DurationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Task Time")

        self.hours_input = QSpinBox()
        self.hours_input.setRange(0, 23)

        self.minutes_input = QSpinBox()
        self.minutes_input.setRange(0, 59)
        self.minutes_input.setSingleStep(10)

        form_layout = QFormLayout()
        form_layout.addRow("H", self.hours_input)
        form_layout.addRow("M", self.minutes_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(buttons)

    @property
    def duration_minutes(self) -> int:
        return self.hours_input.value() * 60 + self.minutes_input.value()

    def set_duration(self, minutes: int):
        self.hours_input.setValue(minutes // 60)
        self.minutes_input.setValue(minutes % 60)
