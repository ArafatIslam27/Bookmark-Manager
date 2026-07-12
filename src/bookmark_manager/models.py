from datetime import datetime, timezone
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Relationship


# --- Account Models ---
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str

    # Explicit bidirectional mapping
    bookmarks: list["Bookmark"] = Relationship(back_populates="user")


class UserCreate(BaseModel):
    email: str
    password: str


# --- Bookmark Models ---
class BookmarkBase(SQLModel):
    title: str = Field(index=True)
    url: str    # Enforces that a URL string must be passed


class Bookmark(BookmarkBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Establish the relational ownership link
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="bookmarks")


class BookmarkCreate(BookmarkBase):
    pass    # Used to validate data coming in from the user client