from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from core.constants import GRID_COLUMNS, GRID_ROWS, CELL_SIZE


class TimeTable(QWidget):
    def __init__(self, parent=None, title="TimeTable"):
        super().__init__(parent)
        self.title = title
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Canvas for drawing
        self.canvas = TimeTableCanvas(parent)
        layout.addWidget(self.canvas)
        
        self.setMinimumSize(GRID_COLUMNS * CELL_SIZE + 80, GRID_ROWS * CELL_SIZE + 40)


class TimeTableCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(GRID_COLUMNS * CELL_SIZE + 80, GRID_ROWS * CELL_SIZE + 40)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor("#F8F8F8"))
        pen = QPen(QColor("#CCCCCC"))
        painter.setPen(pen)

        for row in range(GRID_ROWS):
            y = 20 + row * CELL_SIZE
            painter.drawLine(60, y, 60 + GRID_COLUMNS * CELL_SIZE, y)
            painter.drawText(10, y + CELL_SIZE / 2 + 5, f"{row:02d}")

        for col in range(GRID_COLUMNS + 1):
            x = 60 + col * CELL_SIZE
            painter.drawLine(x, 20, x, 20 + GRID_ROWS * CELL_SIZE)
            if col < GRID_COLUMNS:
                painter.drawText(x + CELL_SIZE / 2 - 8, 15, f"{col * 10:02d}")

        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        painter.drawRect(60, 20, GRID_COLUMNS * CELL_SIZE, GRID_ROWS * CELL_SIZE)
