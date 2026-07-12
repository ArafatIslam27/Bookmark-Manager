import os
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from bookmark_manager.database import get_session
from bookmark_manager.models import Bookmark, BookmarkCreate, User, UserCreate

router = APIRouter(tags=["Application Gateway"])

# Fallback string for development; read a cryptographically random block in production
SECRET_KEY = os.getenv(
    "SECRET_KEY", "prod-security-string-change-via-environment-variables"
)
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# --- Authentication Security Logic ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
    payload = data.copy()
    payload.update({"exp": datetime.now(timezone.utc) + expires_delta})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> User:
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Session invalid or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise auth_error
    except jwt.PyJWTError:
        raise auth_error

    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise auth_error
    return user


# --- Registration & Login Endpoints ---
@router.post("/auth/register", status_code=201)
async def register(
    user_data: UserCreate, session: Session = Depends(get_session)
):
    exists = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Account already exists")

    new_user = User(
        email=user_data.email, hashed_password=hash_password(user_data.password)
    )
    session.add(new_user)
    session.commit()
    return {"status": "success", "message": "Account initialized"}


@router.post("/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(
        select(User).where(User.email == form_data.username)
    ).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Invalid credentials entered"
        )

    token = create_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# --- Isolated Application Logic ---
@router.post("/bookmarks/", response_model=Bookmark, status_code=201)
async def add_bookmark(
    data: BookmarkCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    # Inject user ownership directly into database layout context
    db_bookmark = Bookmark.model_validate(data, update={"user_id": user.id})
    session.add(db_bookmark)
    session.commit()
    session.refresh(db_bookmark)
    return db_bookmark


@router.get("/bookmarks/", response_model=list[Bookmark])
async def list_bookmarks(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    # CRITICAL: Enforce strict data multi-tenancy boundaries
    return session.exec(
        select(Bookmark).where(Bookmark.user_id == user.id)
    ).all()