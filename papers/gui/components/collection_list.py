from PySide6 import QtCore, QtGui, QtWidgets

import papers.gui.components.lists
import papers.gui.components.overlays
import papers.models


class CollectionListItem(QtWidgets.QWidget):
    add_paper_requested = QtCore.Signal(int, int)

    def __init__(self, collection: papers.models.Collection):
        super().__init__()

        self.collection = collection

        self.setAcceptDrops(True)
        self.drag_overlay = papers.gui.components.overlays.DragOverlay(self)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel(collection.name))
        self.setLayout(layout)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        source = event.source()
        if isinstance(source, papers.gui.components.lists.ListWidget):
            mime_data = event.mimeData()
            if mime_data.hasFormat('application/x-paper-id'):
                byte_array = mime_data.data('application/x-paper-id')
                paper_id_str = bytes(byte_array.data()).decode()
                self.dragged_paper_id = int(paper_id_str)
                self.drag_overlay.show()
                event.acceptProposedAction()
                return
        event.ignore()

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        self.drag_overlay.hide()
        event.accept()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        self.drag_overlay.hide()

        mime_data = event.mimeData()
        if mime_data.hasFormat('application/x-paper-id'):
            byte_array = mime_data.data('application/x-paper-id')
            paper_id_str = bytes(byte_array.data()).decode()
            paper_id = int(paper_id_str)
            self.add_paper_requested.emit(paper_id, self.collection.id)
        event.accept()


class CollectionListWidget(papers.gui.components.lists.ListWidget):
    add_paper_to_collection_requested = QtCore.Signal(int, int)

    def __init__(self):
        super().__init__()

        self.set_placeholder_text('No collections')

    def insert_collection(self, collection: papers.models.Collection, index: int = 0):
        item = QtWidgets.QListWidgetItem(self)
        assert collection.name is not None
        widget = CollectionListItem(collection)
        widget.add_paper_requested.connect(self.add_paper_to_collection_requested)
        item.setSizeHint(widget.sizeHint())
        self.insertItem(index, item)
        self.setItemWidget(item, widget)
