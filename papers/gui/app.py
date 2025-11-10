from typing import cast

from PySide6 import QtCore, QtGui, QtWidgets

import papers.core.database
import papers.gui.collections
import papers.gui.information
import papers.gui.papers
import papers.models


class ApplicationWindow(QtWidgets.QMainWindow):
    add_paper_requested = QtCore.Signal(str)
    add_collection_requested = QtCore.Signal(str)
    add_paper_to_collection_requested = QtCore.Signal(int, int)
    link_pdf_requested = QtCore.Signal(int, str)
    open_pdf_requested = QtCore.Signal(int)

    def __init__(self):
        super().__init__()

        self.current_paper_id: int | None = None
        self.current_collection_id: int | None = None

        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        self.collections = papers.gui.collections.Collections()
        self.collections.add_collection_requested.connect(self.add_collection_requested)
        self.collections.add_paper_to_collection_requested.connect(self.add_paper_to_collection_requested)
        self.collections.collection_selected.connect(self.collection_selected)
        splitter.addWidget(self.collections)

        self.papers = papers.gui.papers.Papers()
        self.papers.search_text_changed.connect(self.search)
        self.papers.add_requested.connect(self.add_paper_requested)
        self.papers.link_pdf_requested.connect(self.link_pdf_requested)
        self.papers.open_pdf_requested.connect(self.open_pdf_requested)
        self.papers.item_selected.connect(self.paper_selected)
        splitter.addWidget(self.papers)

        self.information = papers.gui.information.Information()
        self.information.notes_updated.connect(self.notes_updated)
        splitter.addWidget(self.information)

        self.collections.setMinimumWidth(100)
        self.papers.setMinimumWidth(200)
        self.information.setMinimumWidth(100)
        splitter.setSizes([1, 5, 2])

        search_shortcut = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+F'), self)
        search_shortcut.activated.connect(self.focus_search_bar)

    def add_paper(self, paper: papers.models.Paper):
        self.papers.insert_paper(paper)

    def add_collection(self, collection: papers.models.Collection):
        self.collections.insert_collection(collection)

    def paper_selected(self, id: int):
        self.current_paper_id = id
        paper = papers.core.database.query_paper(id)
        self.information.notes_view.setPlainText(cast(str, paper.notes) or '')

    def collection_selected(self, id: int | None):
        self.current_collection_id = id
        items = papers.core.database.query_papers(id)
        self.papers.show_only([item.id for item in items if item.id is not None])

    def notes_updated(self, notes: str):
        if self.current_paper_id:
            papers.core.database.update_paper(self.current_paper_id, notes=notes)

    def focus_search_bar(self):
        self.papers.search_box.setFocus()
        self.papers.search_box.selectAll()

    def search(self, text: str):
        if not text:
            self.collection_selected(self.current_collection_id)
            return

        matching_papers = papers.core.database.search_papers(text, self.current_collection_id)
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
