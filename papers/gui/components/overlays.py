from PySide6 import QtCore, QtGui, QtWidgets


class DragOverlay(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget, stroke_width: int = 2):
        super().__init__(parent)

        self.stroke_width = stroke_width

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()

        self.resize(parent.size())
        parent.installEventFilter(self)

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent):
        # Automatically resize when parent resizes
        if isinstance(obj, QtWidgets.QWidget) and obj == self.parent() and event.type() == QtCore.QEvent.Type.Resize:
            self.resize(obj.size())
        return super().eventFilter(obj, event)

    def paintEvent(self, event: QtGui.QPaintEvent):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 122, 204, 38)))
        painter.setPen(QtGui.QPen(QtGui.QColor('#007ACC'), self.stroke_width, QtCore.Qt.PenStyle.DashLine))
        painter.drawRoundedRect(
            self.rect().adjusted(
                self.stroke_width // 2, self.stroke_width // 2, -self.stroke_width // 2, -self.stroke_width // 2
            ),
            3 * self.stroke_width,
            3 * self.stroke_width,
        )
        painter.end()
