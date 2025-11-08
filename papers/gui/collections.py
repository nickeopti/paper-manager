from PySide6 import QtWidgets

import papers.gui.components.search
import papers.gui.components.lists


class Collections(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.search_box = papers.gui.components.search.SearchBox('Search collections')
        layout.addWidget(self.search_box)

        self.collection_list = papers.gui.components.lists.ListWidget()
        self.collection_list.set_placeholder_text('No collections')
        layout.addWidget(self.collection_list)

        add_button = QtWidgets.QPushButton('+')
        add_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        layout.addWidget(add_button)
