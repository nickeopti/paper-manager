from PySide6 import QtCore, QtWidgets

import papers.gui.components.paper_list
import papers.gui.components.search


class Papers(QtWidgets.QWidget):
    add_requested = QtCore.Signal(str)
    link_pdf_requested = QtCore.Signal(int, str)
    open_pdf_requested = QtCore.Signal(int)
    item_selected = QtCore.Signal(int)
    search_text_changed = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.search_box = papers.gui.components.search.SearchBox('Search papers')
        self.search_box.textChanged.connect(self.search_text_changed)
        layout.addWidget(self.search_box)

        self.paper_list = papers.gui.components.paper_list.PaperListWidget()
        self.paper_list.add_requested.connect(self.add_requested)
        self.paper_list.link_pdf_requested.connect(self.link_pdf_requested)
        self.paper_list.open_pdf_requested.connect(self.open_pdf_requested)
        self.paper_list.item_selected.connect(self.item_selected)
        layout.addWidget(self.paper_list)

    def show_all(self):
        self.paper_list.show_all()

    def show_only(self, ids: list[int]):
        self.paper_list.show_only(ids)
