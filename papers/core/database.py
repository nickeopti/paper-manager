from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

import papers.configuration


class Base(DeclarativeBase):
    pass


class Paper(Base):
    __tablename__ = 'papers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reference = Column(String, nullable=True)
    bib_path = Column(String, nullable=True)
    pdf_path = Column(String, nullable=True)
    title = Column(String, nullable=True)
    authors = Column(String, nullable=True)
    date = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    pdf_text = Column(Text, nullable=True)


_engine: Engine | None = None
_Session: sessionmaker[Session] = None  # type: ignore


def _init():
    global _engine, _Session
    if _engine is None:
        db_path = papers.configuration.configuration.root_directory / 'papers.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(_engine)
        _Session = sessionmaker(bind=_engine)


def insert(
    reference: str | None = None,
    title: str | None = None,
    authors: str | None = None,
    date: str | None = None,
    bib_path: str | None = None,
    pdf_path: str | None = None,
    notes: str | None = None,
    pdf_text: str | None = None,
):
    _init()
    session = _Session()
    paper = Paper(
        reference=reference,
        title=title,
        authors=authors,
        date=date,
        bib_path=str(bib_path) if bib_path else None,
        pdf_path=str(pdf_path) if pdf_path else None,
        notes=notes,
        pdf_text=pdf_text,
    )
    session.add(paper)
    session.commit()
    session.refresh(paper)
    session.expunge(paper)
    session.close()
    return paper


def update(
    id: int,
    title: str | None = None,
    authors: str | None = None,
    date: str | None = None,
    bib_path: str | None = None,
    pdf_path: str | None = None,
    notes: str | None = None,
    pdf_text: str | None = None,
):
    _init()
    session = _Session()
    paper = session.query(Paper).filter(Paper.id == id).first()
    if paper:
        if title is not None:
            paper.title = title  # type: ignore
        if authors is not None:
            paper.authors = authors  # type: ignore
        if date is not None:
            paper.date = date  # type: ignore
        if bib_path is not None:
            paper.bib_path = bib_path  # type: ignore
        if pdf_path is not None:
            paper.pdf_path = pdf_path  # type: ignore
        if notes is not None:
            paper.notes = notes  # type: ignore
        if pdf_text is not None:
            paper.pdf_text = pdf_text  # type: ignore
        session.commit()
        session.refresh(paper)
        session.expunge(paper)
    session.close()
    return paper


def query(id: int | None = None, title: str | None = None, authors: str | None = None, date: str | None = None):
    _init()
    session = _Session()
    q = session.query(Paper)
    if id is not None:
        q = q.filter(Paper.id == id)
    if title:
        q = q.filter(Paper.title.ilike(f'%{title}%'))
    if authors:
        q = q.filter(Paper.authors.ilike(f'%{authors}%'))
    if date:
        q = q.filter(Paper.date == date)
    result = q.all()
    for paper in result:
        session.expunge(paper)
    session.close()
    return result


def search(query: str):
    _init()
    session = _Session()
    search_string = f'%{query}%'
    q = session.query(Paper).filter(
        (Paper.title.ilike(search_string))
        | (Paper.authors.ilike(search_string))
        | (Paper.notes.ilike(search_string))
        | (Paper.pdf_text.ilike(search_string))
    )
    result = q.all()
    for paper in result:
        session.expunge(paper)
    session.close()
    return result
