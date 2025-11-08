from PySide6 import QtCore, QtWidgets


class Information(QtWidgets.QWidget):
    notes_updated = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.notes_view = QtWidgets.QTextEdit()
        self.notes_view.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.notes_view.textChanged.connect(lambda: self.notes_updated.emit(self.notes_view.toPlainText()))
        layout.addWidget(self.notes_view)
