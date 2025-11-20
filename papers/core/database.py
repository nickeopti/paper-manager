import sys
from pathlib import Path
from typing import Any

import sqlalchemy as sqla
from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, Text

import papers.configuration
import papers.models

if 'production' not in sys.argv[1:]:
    papers.configuration.configuration.root_directory = Path('.papers')

db_path = papers.configuration.configuration.root_directory / 'papers.db'
db_path.parent.mkdir(parents=True, exist_ok=True)

engine = sqla.create_engine(f'sqlite:///{db_path}', echo='production' not in sys.argv[1:])

metadata = MetaData()

paper_table = Table(
    'paper',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('reference', String, nullable=True),
    Column('bib_path', String, nullable=True),
    Column('pdf_path', String, nullable=True),
    Column('title', String, nullable=True),
    Column('authors', String, nullable=True),
    Column('date', String, nullable=True),
    Column('notes', Text, nullable=True),
    Column('pdf_text', Text, nullable=True),
)

collection_table = Table(
    'collection',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, nullable=False),
)

paper_collection_table = Table(
    'paper_collection',
    metadata,
    Column('paper_id', Integer, ForeignKey('paper.id', ondelete='CASCADE'), primary_key=True),
    Column('collection_id', Integer, ForeignKey('collection.id', ondelete='CASCADE'), primary_key=True),
)


metadata.create_all(engine, checkfirst=True)


def insert_paper(paper: papers.models.Paper) -> int:
    with engine.begin() as connection:
        result = connection.execute(
            sqla.insert(paper_table),
            {
                'reference': paper.reference,
                'title': paper.title,
                'authors': paper.authors,
                'date': paper.date,
                'bib_path': paper.bib_path,
                'pdf_path': paper.pdf_path,
                'notes': paper.notes,
                'pdf_text': paper.pdf_text,
            },
        )
    assert result.inserted_primary_key is not None
    (key,) = result.inserted_primary_key
    print('inserted paper with id', key)
    return key


def update_paper(paper_id: int, **fields: Any) -> None:
    with engine.begin() as connection:
        connection.execute(
            sqla.update(paper_table).where(paper_table.c.id == paper_id).values(**fields),
        )


def remove_paper(paper_id: int) -> None:
    with engine.begin() as connection:
        connection.execute(
            sqla.delete(paper_table).where(paper_table.c.id == paper_id),
        )


def insert_collection(collection: papers.models.Collection) -> int:
    with engine.begin() as connection:
        result = connection.execute(
            sqla.insert(collection_table),
            {
                'name': collection.name,
            },
        )
    assert result.inserted_primary_key is not None
    assert len(result.inserted_primary_key) == 1

    return result.inserted_primary_key[0]


def update_collection(collection: papers.models.Collection) -> None:
    with engine.begin() as connection:
        connection.execute(
            sqla.update(collection_table)
            .where(collection_table.c.id == collection.id)
            .values(**{k: v for k, v in vars(collection).items() if k != 'id' and v is not None}),
        )


def remove_collection(collection_id: int) -> None:
    with engine.begin() as connection:
        connection.execute(
            sqla.delete(collection_table).where(collection_table.c.id == collection_id),
        )


def add_paper_to_collection(paper_id: int, collection_id: int) -> None:
    with engine.begin() as connection:
        # Check if the relationship already exists
        existing = connection.execute(
            sqla.select(paper_collection_table).where(
                paper_collection_table.c.paper_id == paper_id,
                paper_collection_table.c.collection_id == collection_id,
            )
        ).first()

        # Only insert if it doesn't already exist
        if existing is None:
            connection.execute(
                sqla.insert(paper_collection_table),
                {
                    'paper_id': paper_id,
                    'collection_id': collection_id,
                },
            )


def remove_paper_from_collection(paper_id: int, collection_id: int) -> None:
    with engine.begin() as connection:
        connection.execute(
            sqla.delete(paper_collection_table).where(
                paper_collection_table.c.paper_id == paper_id,
                paper_collection_table.c.collection_id == collection_id,
            ),
        )


def query_paper(paper_id: int) -> papers.models.Paper:
    with engine.connect() as connection:
        result = connection.execute(sqla.select(paper_table).where(paper_table.c.id == paper_id)).first()
    if result is None:
        raise ValueError(f'Paper with id {paper_id} not found')
    return papers.models.Paper(**result._asdict())


def query_papers(collection_id: int | None = None) -> list[papers.models.Paper]:
    with engine.connect() as connection:
        query = sqla.select(paper_table)
        if collection_id is not None:
            query = query.join(paper_collection_table).filter(paper_collection_table.c.collection_id == collection_id)
        result = connection.execute(query)
    return [papers.models.Paper(**row._asdict()) for row in result]


def query_collections(paper_id: int | None = None) -> list[papers.models.Collection]:
    with engine.connect() as connection:
        query = sqla.select(collection_table)
        if paper_id is not None:
            query = query.join(paper_collection_table).filter(paper_collection_table.c.paper_id == paper_id)
        result = connection.execute(query)
    return [papers.models.Collection(**row._asdict()) for row in result]


def search_papers(query_string: str, collection_id: int | None = None) -> list[papers.models.Paper]:
    with engine.connect() as connection:
        query = sqla.select(paper_table)
        if collection_id is not None:
            query = query.join(paper_collection_table).filter(paper_collection_table.c.collection_id == collection_id)
        query = query.filter(
            paper_table.c.title.ilike(f'%{query_string}%')
            | paper_table.c.authors.ilike(f'%{query_string}%')
            | paper_table.c.notes.ilike(f'%{query_string}%')
            | paper_table.c.pdf_text.ilike(f'%{query_string}%')
        )
        result = connection.execute(query)
    return [papers.models.Paper(**row._asdict()) for row in result]
