import os
import shutil
import sys
from pathlib import Path
from typing import cast

from PySide6 import QtWidgets

import papers.configuration
import papers.core.bib
import papers.core.database
import papers.core.pdf
import papers.gui.app


def main():
    app = QtWidgets.QApplication()
    window = papers.gui.app.create_app()

    entries = papers.core.database.query()
    for entry in entries:
        window.add_paper(entry)

    def add_paper_to_database(path: str) -> papers.core.database.Paper:
        info = papers.core.bib.parse_bib_file(path)
        entry = papers.core.database.insert(
            reference=info.reference,
            title=info.title,
            authors=', '.join(info.authors),
            date=info.date,
            bib_path=path,
        )
        window.add_paper(entry)

        bib_path = papers.configuration.configuration.root_directory / str(entry.id) / Path(path).name
        bib_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(path, bib_path)

        return entry

    window.add_paper_to_database_requested.connect(add_paper_to_database)

    window.link_pdf_requested.connect(link_pdf)
    window.open_pdf_requested.connect(open_pdf)

    window.show()
    app.exec()


def link_pdf(id: int, path: str):
    pdf_path = papers.configuration.configuration.root_directory / str(id) / Path(path).name
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path, pdf_path)
    pdf_text = papers.core.pdf.extract_text_from_pdf(str(pdf_path))
    papers.core.database.update(id, pdf_path=str(pdf_path), pdf_text=pdf_text)


def open_pdf(id: int):
    path = cast(str | None, papers.core.database.query(id=id)[0].pdf_path)
    if path:
        if sys.platform.startswith('darwin'):
            os.system(f'open "{path}"')
        elif sys.platform.startswith('win'):
            os.startfile(path)
        else:
            os.system(f'xdg-open "{path}"')


if __name__ == '__main__':
    if 'production' not in sys.argv[1:]:
        papers.configuration.configuration.root_directory = Path('.papers')

    main()
