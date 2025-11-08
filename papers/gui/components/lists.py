from PySide6 import QtCore, QtGui, QtWidgets


class ListWidget(QtWidgets.QListWidget):
    def __init__(self):
        super().__init__()

        self.placeholder_text: str | None = None

        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.setSpacing(2)

    def set_placeholder_text(self, text: str):
        self.placeholder_text = text
        self.repaint()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        super().paintEvent(event)

        if self.count() > 0 or self.placeholder_text is None:
            return

        painter = QtGui.QPainter(self.viewport())
        painter.setPen(QtGui.QPen(self.palette().text().color()))
        painter.drawText(self.viewport().rect(), QtCore.Qt.AlignmentFlag.AlignCenter, self.placeholder_text)
        painter.end()
