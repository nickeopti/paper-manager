from typing import cast

from PySide6 import QtCore, QtGui, QtWidgets

import papers.core.database
import papers.gui.collections
import papers.gui.information
import papers.gui.papers


class ApplicationWindow(QtWidgets.QMainWindow):
    add_paper_to_database_requested = QtCore.Signal(str)
    link_pdf_requested = QtCore.Signal(int, str)
    open_pdf_requested = QtCore.Signal(int)

    def __init__(self):
        super().__init__()

        self.current_paper_id: int | None = None

        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        self.collections = papers.gui.collections.Collections()
        splitter.addWidget(self.collections)

        self.papers = papers.gui.papers.Papers()
        self.papers.search_text_changed.connect(self.search)
        self.papers.add_requested.connect(self.add_paper_to_database_requested)
        self.papers.link_pdf_requested.connect(self.link_pdf_requested)
        self.papers.open_pdf_requested.connect(self.open_pdf_requested)
        self.papers.item_selected.connect(self.item_selected)
        splitter.addWidget(self.papers)

        self.information = papers.gui.information.Information()
        self.information.notes_updated.connect(self.notes_updated)
        splitter.addWidget(self.information)

        self.collections.setMinimumWidth(100)
        self.papers.setMinimumWidth(200)
        self.information.setMinimumWidth(100)
        splitter.setSizes([1, 5, 2])

    def add_paper(self, paper: papers.core.database.Paper):
        self.papers.paper_list.insert_paper(paper.id, paper.reference, paper.title, paper.authors, paper.date)  # type: ignore

    def item_selected(self, id: int):
        self.current_paper_id = id
        paper = papers.core.database.query(id=id)[0]
        self.information.notes_view.setPlainText(cast(str, paper.notes) or '')

    def notes_updated(self, notes: str):
        if self.current_paper_id:
            papers.core.database.update(self.current_paper_id, notes=notes)

    def search(self, text: str):
        if not text:
            self.papers.show_all()
            return

        matching_papers = papers.core.database.search(text)
        ids = [cast(int, paper.id) for paper in matching_papers]
        self.papers.show_only(ids)


def create_app(*args, **kwargs):
    window = ApplicationWindow(*args, **kwargs)
    window.setWindowTitle('Papers')
    window.resize(1500, 900)

    pixmap = QtGui.QPixmap(32, 32)
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)
    window.setWindowIcon(QtGui.QIcon(pixmap))

    return window
