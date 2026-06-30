from collections.abc import Generator
from sqlmodel import Session, create_engine, SQLModel

sqlite_url = "sqlite:///./bookmarks.db"

# echo=True allows you to see the auto-generated SQL in your console for debugging
engine = create_engine(sqlite_url, echo=True)

def init_db() -> None:
    """Creates the database and tables if they don't exist."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Provides a transactional database session context to our endpoints."""
    with Session(engine) as session:
        yield session