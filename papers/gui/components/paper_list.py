from typing import cast

from PySide6 import QtCore, QtGui, QtWidgets

import papers.gui.components.lists
import papers.gui.components.overlays
import papers.models


class PaperListItem(QtWidgets.QWidget):
    link_pdf_requested = QtCore.Signal(str)

    def __init__(self, reference: str, title: str, authors: str, date: str):
        super().__init__()

        self.reference = reference

        self.setAcceptDrops(True)
        self.drag_overlay = papers.gui.components.overlays.DragOverlay(self)

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)

        title_label = QtWidgets.QLabel(title)
        layout.addWidget(title_label, 0, 0)

        authors_label = QtWidgets.QLabel(authors)
        authors_label.setStyleSheet('color: #666666;')
        layout.addWidget(authors_label, 1, 0)

        date_label = QtWidgets.QLabel(date)
        date_label.setStyleSheet('color: #666666;')
        layout.addWidget(date_label, 1, 1, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        spacer = QtWidgets.QSpacerItem(8, 1)
        layout.addItem(spacer, 0, 2, 2, 1)

        self.setLayout(layout)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        print(event.key())
        if event.key() == QtCore.Qt.Key.Key_C and event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            print(self.reference)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].path().endswith('.pdf'):
                self.drag_overlay.show()
                event.acceptProposedAction()

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        self.drag_overlay.hide()
        event.accept()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        self.drag_overlay.hide()
        self.link_pdf_requested.emit(event.mimeData().urls()[0].path())
        event.accept()


class PaperListWidget(papers.gui.components.lists.ListWidget):
    remove_requested = QtCore.Signal(str)

    item_selected = QtCore.Signal(int)
    add_requested = QtCore.Signal(str)
    link_pdf_requested = QtCore.Signal(int, str)
    open_pdf_requested = QtCore.Signal(int)

    def __init__(self):
        super().__init__()

        self.set_placeholder_text('Drag and drop .bib file to add paper')

        self.itemSelectionChanged.connect(self.send_selection_changed)

        self.itemDoubleClicked.connect(
            lambda item: self.open_pdf_requested.emit(item.data(QtCore.Qt.ItemDataRole.UserRole))
        )

        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragDrop)
        self.drag_overlay = papers.gui.components.overlays.DragOverlay(self)

        self.setStyleSheet(
            """
            QListWidget {
                outline: none;
            }
            QListWidget::item:selected {
                background: rgba(128, 128, 128, 40);
                border: none;
            }
            QListWidget::item:hover {
                background: rgba(128, 128, 128, 20);
            }
            """
        )

    def insert_paper(self, paper: papers.models.Paper, index: int = 0):
        item = QtWidgets.QListWidgetItem(self)
        widget = PaperListItem(paper.reference or '', paper.title or '', paper.authors or '', paper.date or '')
        widget.link_pdf_requested.connect(lambda path: self.link_pdf_requested.emit(paper.id, path))
        item.setSizeHint(widget.sizeHint())
        self.insertItem(index, item)
        self.setItemWidget(item, widget)
        item.setData(QtCore.Qt.ItemDataRole.UserRole, paper.id)

    def show_all(self):
        for i in range(self.count()):
            item = self.item(i)
            item.setHidden(False)

    def show_only(self, ids: list[int]):
        for i in range(self.count()):
            item = self.item(i)
            item.setHidden(item.data(QtCore.Qt.ItemDataRole.UserRole) not in ids)

    def send_selection_changed(self):
        selection = self.selectedItems()
        if selection:
            item = selection[0]
            self.item_selected.emit(item.data(QtCore.Qt.ItemDataRole.UserRole))

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_C and event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            item = self.selectedItems()[0]
            widget = cast(PaperListItem, self.itemWidget(item))
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(widget.reference)
        elif event.key() == QtCore.Qt.Key.Key_Return:
            item = self.selectedItems()[0]
            self.open_pdf_requested.emit(item.data(QtCore.Qt.ItemDataRole.UserRole))
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        """Show context menu for list items."""
        item = self.itemAt(event.pos())
        if item is None:
            return

        menu = QtWidgets.QMenu()
        menu.addAction(
            'Remove from Recent Projects',
            lambda: self.remove_requested.emit(item.data(QtCore.Qt.ItemDataRole.UserRole)),
        )
        menu.exec(event.globalPos())

        event.accept()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].path().endswith('.bib'):
                self.drag_overlay.show()
                event.acceptProposedAction()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].path().endswith('.bib'):
                event.acceptProposedAction()

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent) -> None:
        self.drag_overlay.hide()
        event.accept()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        self.drag_overlay.hide()
        path = event.mimeData().urls()[0].path()
        self.add_requested.emit(path)

        event.accept()

    def mimeData(self, items: list[QtWidgets.QListWidgetItem]) -> QtCore.QMimeData:
        mime_data = super().mimeData(items)
        if items:
            item = items[0]
            paper_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
            if paper_id is not None:
                mime_data.setData('application/x-paper-id', str(paper_id).encode())
        return mime_data
