import dataclasses


@dataclasses.dataclass
class Paper:
    id: int | None = None
    reference: str | None = None
    bib_path: str | None = None
    pdf_path: str | None = None
    title: str | None = None
    authors: str | None = None
    date: str | None = None
    notes: str | None = None
    pdf_text: str | None = None


@dataclasses.dataclass
class Collection:
    id: int | None = None
    name: str | None = None
