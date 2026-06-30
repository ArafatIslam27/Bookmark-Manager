from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from bookmark_manager.database import get_session
from bookmark_manager.models import Bookmark, BookmarkCreate

router = APIRouter(prefix='/bookmarks', tags=['Bookmarks'])

@router.post('/', response_model=Bookmark, status_code=201)
async def create_bookmark(bookmark_data: BookmarkCreate, session: Session = Depends(get_session)):
    # Map incoming schema to the database Table model
    db_bookmark = Bookmark.model_validate(bookmark_data)
    session.add(db_bookmark)
    session.commit()
    session.refresh(db_bookmark)
    return db_bookmark

@router.get('/', response_model=list[Bookmark])
async def read_bookmarks(session: Session = Depends(get_session)):
    bookmarks = session.exec(select(Bookmark)).all()
    return bookmarks