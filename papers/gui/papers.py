import tempfile

from PySide6 import QtCore, QtGui, QtWidgets

import papers.gui.components.paper_list
import papers.gui.components.search
import papers.models


class BibDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Add Paper')
        self.resize(600, 400)

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        self.text_edit = QtWidgets.QTextEdit(self)
        layout.addWidget(self.text_edit)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def get_text(self):
        return self.text_edit.toPlainText().strip()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_Return and event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            self.accept()
        elif event.key() == QtCore.Qt.Key.Key_Escape:
            self.reject()

    @classmethod
    def get_bib_text(cls) -> str | None:
        dialog = cls()
        result = dialog.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            return dialog.get_text()
        else:
            return None


class Papers(QtWidgets.QWidget):
    add_requested = QtCore.Signal(str)
    remove_requested = QtCore.Signal(int)
    link_pdf_requested = QtCore.Signal(int, str)
    open_pdf_requested = QtCore.Signal(int)
    item_selected = QtCore.Signal(int)
    search_text_changed = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.search_box = papers.gui.components.search.SearchBox('Search papers')
        self.search_box.textChanged.connect(self.search_text_changed)
        layout.addWidget(self.search_box)

        self.paper_list = papers.gui.components.paper_list.PaperListWidget()
        self.paper_list.add_requested.connect(self.add_requested)
        self.paper_list.remove_requested.connect(self.remove_requested)
        self.paper_list.link_pdf_requested.connect(self.link_pdf_requested)
        self.paper_list.open_pdf_requested.connect(self.open_pdf_requested)
        self.paper_list.item_selected.connect(self.item_selected)
        layout.addWidget(self.paper_list)

        add_button = QtWidgets.QPushButton('+')
        add_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        add_button.clicked.connect(self._add_paper_manually)
        layout.addWidget(add_button)

    def insert_paper(self, paper: papers.models.Paper):
        self.paper_list.insert_paper(paper)

    def remove_paper(self, id: int):
        self.paper_list.remove_paper(id)

    def show_all(self):
        self.paper_list.show_all()

    def show_only(self, ids: list[int]):
        self.paper_list.show_only(ids)

    def _add_paper_manually(self):
        text = BibDialog.get_bib_text()
        if not text:
            return

        with tempfile.NamedTemporaryFile(suffix='.bib') as temp_file:
            temp_file.write(text.encode('utf-8'))
            temp_file.flush()
            self.add_requested.emit(temp_file.name)
