from datetime import datetime, timezone
from sqlmodel import Field, SQLModel

class BookmarkBase(SQLModel):
    title: str = Field(index=True)
    url: str    # Enforces that a URL string must be passed

class Bookmark(BookmarkBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BookmarkCreate(BookmarkBase):
    pass    # Used to validate data coming in from the user client