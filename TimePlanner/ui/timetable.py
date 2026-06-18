from PySide6.QtCore import QMimeData, QPoint, Qt
from PySide6.QtGui import QBrush, QColor, QDrag, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.constants import CELL_SIZE, GRID_COLUMNS, GRID_ROWS
from ui.task_item import TASK_MIME_TYPE


class TimeTable(QWidget):
    def __init__(self, parent=None, title="TimeTable"):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("tableTitle")
        layout.addWidget(self.title_label)

        self.canvas = TimeTableCanvas(parent)
        layout.addWidget(self.canvas)

        self.setMinimumSize(GRID_COLUMNS * CELL_SIZE + 80, GRID_ROWS * CELL_SIZE + 72)


class TimeTableCanvas(QWidget):
    left_margin = 60
    top_margin = 20

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = []
        self.blocks = []
        self.start_cell = 0
        self.drag_start_position = QPoint()
        self.drag_block = None
        self.preview_task_id = None
        self.preview_start = None

        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setMinimumSize(GRID_COLUMNS * CELL_SIZE + 80, GRID_ROWS * CELL_SIZE + 40)
        self.setCursor(Qt.ArrowCursor)

    def set_data(self, tasks, blocks, start_cell):
        self.tasks = tasks
        self.blocks = blocks
        self.start_cell = start_cell
        self.update()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(TASK_MIME_TYPE):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if not event.mimeData().hasFormat(TASK_MIME_TYPE):
            return

        cell = self.cell_at(event.position().toPoint())
        if cell is None:
            self.clear_preview()
            return

        self.preview_task_id = int(bytes(event.mimeData().data(TASK_MIME_TYPE)).decode("utf-8"))
        self.preview_start = cell
        self.update()
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.clear_preview()

    def dropEvent(self, event):
        cell = self.cell_at(event.position().toPoint())
        if cell is None or not event.mimeData().hasFormat(TASK_MIME_TYPE):
            return

        task_id = int(bytes(event.mimeData().data(TASK_MIME_TYPE)).decode("utf-8"))
        window = self.window()
        if hasattr(window, "place_task_at"):
            if window.place_task_at(task_id, cell):
                event.acceptProposedAction()
        self.clear_preview()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()
            cell = self.cell_at(self.drag_start_position)
            self.drag_block = self.block_at(cell)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        cell = self.cell_at(event.position().toPoint())
        self.setCursor(Qt.OpenHandCursor if self.block_at(cell) is not None else Qt.ArrowCursor)

        if not event.buttons() & Qt.LeftButton or self.drag_block is None:
            return

        distance = (event.position().toPoint() - self.drag_start_position).manhattanLength()
        if distance < 8:
            return

        mime_data = QMimeData()
        mime_data.setData(TASK_MIME_TYPE, str(self.drag_block.task_id).encode("utf-8"))

        drag = QDrag(self)
        drag.setMimeData(mime_data)

        pixmap = QPixmap(CELL_SIZE * 2, CELL_SIZE)
        pixmap.fill(QColor(255, 255, 255, 0))
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(CELL_SIZE // 2, CELL_SIZE // 2))
        drag.exec(Qt.MoveAction)
        self.drag_block = None

    def mouseReleaseEvent(self, event):
        self.drag_block = None
        super().mouseReleaseEvent(event)

    def cell_at(self, point):
        x = point.x() - self.left_margin
        y = point.y() - self.top_margin
        if x < 0 or y < 0:
            return None

        col = x // CELL_SIZE
        row = y // CELL_SIZE
        if col >= GRID_COLUMNS or row >= GRID_ROWS:
            return None
        return self.start_cell + row * GRID_COLUMNS + col

    def block_at(self, cell):
        if cell is None:
            return None
        return next((block for block in self.blocks if block.start <= cell < block.start + block.length), None)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor("#F7F9FC"))
        self.draw_grid(painter)
        self.draw_preview(painter)
        self.draw_blocks(painter)

    def draw_grid(self, painter):
        painter.setFont(QFont("Arial", 9))
        painter.setPen(QPen(QColor("#B8C2CC")))
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.drawRoundedRect(
            self.left_margin,
            self.top_margin,
            GRID_COLUMNS * CELL_SIZE,
            GRID_ROWS * CELL_SIZE,
            6,
            6,
        )

        for row in range(GRID_ROWS):
            y = self.top_margin + row * CELL_SIZE
            hour = (self.start_cell // GRID_COLUMNS) + row
            painter.setPen(QPen(QColor("#52616B")))
            painter.drawText(12, y + CELL_SIZE // 2 + 5, f"{hour:02d}:00")
            painter.setPen(QPen(QColor("#E0E6ED")))
            painter.drawLine(self.left_margin, y, self.left_margin + GRID_COLUMNS * CELL_SIZE, y)

        for col in range(GRID_COLUMNS + 1):
            x = self.left_margin + col * CELL_SIZE
            painter.setPen(QPen(QColor("#E0E6ED")))
            painter.drawLine(x, self.top_margin, x, self.top_margin + GRID_ROWS * CELL_SIZE)
            if col < GRID_COLUMNS:
                painter.setPen(QPen(QColor("#7B8794")))
                painter.drawText(x + CELL_SIZE // 2 - 8, 15, f"{col * 10:02d}")

    def draw_blocks(self, painter):
        task_by_id = {task.id: task for task in self.tasks}
        end_cell = self.start_cell + GRID_ROWS * GRID_COLUMNS

        painter.setFont(QFont("Arial", 9, QFont.Bold))
        for block in self.blocks:
            visible_start = max(block.start, self.start_cell)
            visible_end = min(block.start + block.length, end_cell)
            if visible_start >= visible_end:
                continue

            task = task_by_id.get(block.task_id)
            if task is None:
                continue

            painter.setPen(QPen(QColor("#FFFFFF"), 1))
            for cell in range(visible_start, visible_end):
                local_cell = cell - self.start_cell
                row = local_cell // GRID_COLUMNS
                col = local_cell % GRID_COLUMNS
                x = self.left_margin + col * CELL_SIZE
                y = self.top_margin + row * CELL_SIZE
                painter.setBrush(QBrush(QColor(task.color)))
                painter.drawRoundedRect(x + 3, y + 3, CELL_SIZE - 6, CELL_SIZE - 6, 6, 6)

            first_local = visible_start - self.start_cell
            first_row = first_local // GRID_COLUMNS
            first_col = first_local % GRID_COLUMNS
            painter.setPen(QPen(QColor("#1F2933")))
            painter.drawText(
                self.left_margin + first_col * CELL_SIZE + 6,
                self.top_margin + first_row * CELL_SIZE + 24,
                task.name[:7],
            )

    def draw_preview(self, painter):
        if self.preview_task_id is None or self.preview_start is None:
            return

        task = self.task_by_id(self.preview_task_id)
        if task is None:
            return

        length = max(1, (task.duration + 9) // 10) if task.duration > 0 else 1
        end_cell = self.start_cell + GRID_ROWS * GRID_COLUMNS
        visible_start = max(self.preview_start, self.start_cell)
        visible_end = min(self.preview_start + length, end_cell)
        if visible_start >= visible_end:
            return

        painter.save()
        painter.setOpacity(0.45)
        painter.setBrush(QBrush(QColor(task.color)))
        painter.setPen(QPen(QColor(task.color).darker(125), 2))

        for cell in range(visible_start, visible_end):
            local_cell = cell - self.start_cell
            row = local_cell // GRID_COLUMNS
            col = local_cell % GRID_COLUMNS
            x = self.left_margin + col * CELL_SIZE
            y = self.top_margin + row * CELL_SIZE
            painter.drawRoundedRect(x + 3, y + 3, CELL_SIZE - 6, CELL_SIZE - 6, 6, 6)

        painter.restore()

    def task_by_id(self, task_id):
        return next((task for task in self.tasks if task.id == task_id), None)

    def clear_preview(self):
        if self.preview_task_id is not None or self.preview_start is not None:
            self.preview_task_id = None
            self.preview_start = None
            self.update()
