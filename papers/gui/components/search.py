from PySide6 import QtCore, QtGui, QtWidgets


class SearchIcon(QtGui.QIcon):
    """Custom search icon with configurable color."""

    def __init__(self, color=None):
        super().__init__()
        pixmap = self._create_search_pixmap(color)
        self.addPixmap(pixmap)

    def _create_search_pixmap(self, color: QtGui.QColor | None = None, size: int = 64):
        pixmap = QtGui.QPixmap(size, size)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        if color is None:
            color = QtWidgets.QApplication.palette().text().color()

        pen = QtGui.QPen(color)
        pen.setWidth(4)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        painter.drawEllipse(6, 6, 38, 38)
        painter.drawLine(38, 38, 54, 54)

        painter.end()
        return pixmap


class SearchBox(QtWidgets.QLineEdit):
    """Search box with custom icon."""

    _style_sheet = """
        QLineEdit {
            border-radius: 5px;
            padding: 5px 10px;
        }
    """

    def __init__(self, placeholder: str):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setMinimumWidth(300)

        search_icon = SearchIcon()
        self.addAction(search_icon, QtWidgets.QLineEdit.ActionPosition.LeadingPosition)

        self.setStyleSheet(self._style_sheet)

    def changeEvent(self, event: QtCore.QEvent) -> None:
        super().changeEvent(event)
        match event.type():
            case QtCore.QEvent.Type.PaletteChange:
                self.actions()[0].setIcon(SearchIcon(self.palette().text().color()))

                # Reset style, which updates colours
                self.setStyleSheet(self._style_sheet)
