from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.core.config import get_settings
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)
from app.db.session import get_db
from app.models import User, UserSession
from app.schemas.auth import AuthCredentials, UserPreferencesUpdate, UserResponse

router = APIRouter(prefix="/auth")
settings = get_settings()


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_max_age_seconds,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


async def issue_session(db: AsyncSession, user: User) -> str:
    token = create_session_token()
    db.add(
        UserSession(
            token_hash=hash_session_token(token),
            user_id=user.id,
            expires_at=datetime.now(UTC) + timedelta(seconds=settings.session_max_age_seconds),
        )
    )
    await db.commit()
    return token


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    credentials: AuthCredentials,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> User:
    email = str(credentials.email).strip().lower()
    existing = await db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=email, password_hash=hash_password(credentials.password))
    db.add(user)
    try:
        await db.flush()
        token = await issue_session(db, user)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from exc

    set_session_cookie(response, token)
    return user


@router.post("/login", response_model=UserResponse)
async def login(
    credentials: AuthCredentials,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> User:
    email = str(credentials.email).strip().lower()
    user = await db.scalar(select(User).where(User.email == email))
    password_matches = verify_password(
        credentials.password,
        user.password_hash if user is not None else DUMMY_PASSWORD_HASH,
    )
    if user is None or not password_matches:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = await issue_session(db, user)
    set_session_cookie(response, token)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> None:
    token = request.cookies.get(settings.session_cookie_name)
    if token:
        await db.execute(
            delete(UserSession).where(UserSession.token_hash == hash_session_token(token))
        )
        await db.commit()

    response.delete_cookie(
        key=settings.session_cookie_name,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> User:
    return current_user


@router.patch("/me/preferences", response_model=UserResponse)
async def update_preferences(
    payload: UserPreferencesUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> User:
    current_user.cefr_level = payload.cefr_level
    current_user.learning_goal = payload.learning_goal
    await db.commit()
    await db.refresh(current_user)
    return current_user
