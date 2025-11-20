import os
import shutil
import sys
from pathlib import Path

from PySide6 import QtWidgets

import papers.configuration
import papers.core.bib
import papers.core.database
import papers.core.pdf
import papers.gui.app
import papers.models


def main():
    app = QtWidgets.QApplication()
    window = papers.gui.app.create_app()

    entries = papers.core.database.query_papers()
    for entry in sorted(entries, key=lambda x: x.id or -1, reverse=False):
        window.add_paper(entry)

    entries = papers.core.database.query_collections()
    for entry in entries:
        window.add_collection(entry)

    def add_paper(path: str) -> None:
        paper = papers.core.bib.parse_bib_file(path)
        paper.id = papers.core.database.insert_paper(paper)

        window.add_paper(paper)

        bib_path = papers.configuration.configuration.root_directory / str(paper.id) / Path(path).name
        bib_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(path, bib_path)

    def remove_paper(id: int) -> None:
        papers.core.database.remove_paper(id)
        window.remove_paper(id)

    def add_collection(name: str) -> None:
        collection = papers.models.Collection(name=name)
        collection.id = papers.core.database.insert_collection(collection)

        window.add_collection(collection)

    def add_paper_to_collection(paper_id: int, collection_id: int) -> None:
        papers.core.database.add_paper_to_collection(paper_id, collection_id)

    window.add_paper_requested.connect(add_paper)
    window.remove_paper_requested.connect(remove_paper)
    window.add_collection_requested.connect(add_collection)
    window.add_paper_to_collection_requested.connect(add_paper_to_collection)
    window.link_pdf_requested.connect(link_pdf)
    window.open_pdf_requested.connect(open_pdf)

    window.show()
    app.exec()


def link_pdf(id: int, path: str):
    pdf_path = papers.configuration.configuration.root_directory / str(id) / Path(path).name
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path, pdf_path)
    pdf_text = papers.core.pdf.extract_text_from_pdf(str(pdf_path))
    papers.core.database.update_paper(id, pdf_path=str(pdf_path), pdf_text=pdf_text)


def open_pdf(id: int):
    path = papers.core.database.query_paper(id).pdf_path
    if path:
        if sys.platform.startswith('darwin'):
            os.system(f'open "{path}"')
        elif sys.platform.startswith('win'):
            os.startfile(path)
        else:
            os.system(f'xdg-open "{path}"')


if __name__ == '__main__':
    main()
