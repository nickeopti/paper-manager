from typing import cast

from PySide6 import QtCore, QtWidgets

import papers.gui.components.collection_list
import papers.gui.components.lists
import papers.gui.components.search
import papers.models


class Collections(QtWidgets.QWidget):
    add_collection_requested = QtCore.Signal(str)
    add_paper_to_collection_requested = QtCore.Signal(int, int)
    collection_selected = QtCore.Signal(object)  # int | None

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.search_box = papers.gui.components.search.SearchBox('Search collections')
        layout.addWidget(self.search_box)

        self.collection_list = papers.gui.components.collection_list.CollectionListWidget()
        self.collection_list.add_paper_to_collection_requested.connect(self.add_paper_to_collection_requested)
        self.collection_list.itemSelectionChanged.connect(self._collection_selected)
        layout.addWidget(self.collection_list)

        add_button = QtWidgets.QPushButton('+')
        add_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        add_button.clicked.connect(self.add_collection)
        layout.addWidget(add_button)

        self.insert_collection(papers.models.Collection(id=None, name='All'))

    def add_collection(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Add Collection', 'Collection Name:')
        if ok and text.strip():
            self.add_collection_requested.emit(text.strip())

    def insert_collection(self, collection: papers.models.Collection):
        self.collection_list.insert_collection(collection)

    def _collection_selected(self):
        selection = self.collection_list.selectedItems()
        if selection:
            item = selection[0]
            widget = self.collection_list.itemWidget(item)
            assert isinstance(widget, papers.gui.components.collection_list.CollectionListItem)
            self.collection_selected.emit(widget.collection.id)
        else:
            self.collection_selected.emit(None)
