import os
from collections.abc import Generator
from sqlmodel import Session, create_engine, SQLModel

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bookmarks.db")

engine_kwargs = (
    {"connect_args": {"check_same_thread": False}}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(DATABASE_URL, **engine_kwargs)

def init_db() -> None:
    """Creates the database and tables if they don't exist."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Provides a transactional database session context to our endpoints."""
    with Session(engine) as session:
        yield session