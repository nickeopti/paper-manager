from PySide6 import QtCore, QtWidgets

import papers.models


class Information(QtWidgets.QWidget):
    notes_updated = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.notes_view = QtWidgets.QTextEdit()
        self.notes_view.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.notes_view.textChanged.connect(lambda: self.notes_updated.emit(self.notes_view.toPlainText()))
        layout.addWidget(self.notes_view)

        layout.addWidget(QtWidgets.QLabel('Present in collections:'))
        self.collections_label = QtWidgets.QLabel()
        layout.addWidget(self.collections_label)

    def set_notes(self, notes: str):
        self.notes_view.setPlainText(notes)

    def set_collections(self, collections: list[papers.models.Collection]):
        self.collections_label.setText(
            ', '.join([collection.name for collection in collections if collection.name is not None])
        )
