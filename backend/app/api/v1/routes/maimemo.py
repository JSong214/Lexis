from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.core.secret_cipher import SecretCipher, get_secret_cipher
from app.db.session import get_db
from app.models import MaimemoConnection, MaimemoSyncSnapshot, VocabularyProfile
from app.providers.maimemo import MaimemoProviderError, build_maimemo_sync_provider
from app.schemas.maimemo import (
    ConnectionResponse,
    ConnectionUpdate,
    VocabularyProfileResponse,
)

router = APIRouter()
Database = Annotated[AsyncSession, Depends(get_db)]
Cipher = Annotated[SecretCipher | None, Depends(get_secret_cipher)]


def connection_response(connection: MaimemoConnection | None) -> ConnectionResponse:
    if connection is None:
        return ConnectionResponse(
            configured=False,
            provider=None,
            secret_saved=False,
            updated_at=None,
        )
    secret_saved = connection.encrypted_secret is not None
    return ConnectionResponse(
        configured=connection.provider == "mock" or secret_saved,
        provider=connection.provider,
        secret_saved=secret_saved,
        updated_at=connection.updated_at,
    )


@router.get("/maimemo/connection", response_model=ConnectionResponse)
async def get_connection(current_user: CurrentUser, db: Database) -> ConnectionResponse:
    connection = await db.scalar(
        select(MaimemoConnection).where(MaimemoConnection.user_id == current_user.id)
    )
    return connection_response(connection)


@router.put("/maimemo/connection", response_model=ConnectionResponse)
async def update_connection(
    payload: ConnectionUpdate,
    current_user: CurrentUser,
    db: Database,
    cipher: Cipher,
) -> ConnectionResponse:
    connection = await db.scalar(
        select(MaimemoConnection).where(MaimemoConnection.user_id == current_user.id)
    )
    if connection is None:
        connection = MaimemoConnection(user_id=current_user.id, provider=payload.provider)
        db.add(connection)
    else:
        connection.provider = payload.provider

    if payload.secret:
        if cipher is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Secret encryption is not configured",
            )
        connection.encrypted_secret = cipher.encrypt(payload.secret)

    await db.commit()
    await db.refresh(connection)
    return connection_response(connection)


@router.post("/maimemo/sync", response_model=VocabularyProfileResponse)
async def sync_maimemo(
    current_user: CurrentUser,
    db: Database,
    cipher: Cipher,
) -> VocabularyProfile:
    connection = await db.scalar(
        select(MaimemoConnection).where(MaimemoConnection.user_id == current_user.id)
    )
    if connection is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Configure Maimemo before syncing",
        )

    token: str | None = None
    if connection.provider == "maimemo":
        if connection.encrypted_secret is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Save a Maimemo token before syncing",
            )
        if cipher is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Secret encryption is not configured",
            )
        try:
            token = cipher.decrypt(connection.encrypted_secret)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stored Maimemo token could not be decrypted",
            ) from error

    try:
        provider = build_maimemo_sync_provider(connection.provider)
        result = await provider.sync(token)
    except MaimemoProviderError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    snapshot = MaimemoSyncSnapshot(
        user_id=current_user.id,
        connection_id=connection.id,
        provider=provider.name,
        new_words=result.new_words,
        fuzzy_words=result.fuzzy_words,
        mastered_words_sample=result.mastered_words_sample,
        tracked_word_count=result.tracked_word_count,
        daily_finished_count=result.daily_finished_count,
        daily_total_count=result.daily_total_count,
        daily_study_time_ms=result.daily_study_time_ms,
    )
    db.add(snapshot)
    await db.flush()
    profile = VocabularyProfile(
        user_id=current_user.id,
        snapshot_id=snapshot.id,
        new_words=result.new_words,
        fuzzy_words=result.fuzzy_words,
        mastered_words_sample=result.mastered_words_sample,
        tracked_word_count=result.tracked_word_count,
        daily_finished_count=result.daily_finished_count,
        daily_total_count=result.daily_total_count,
        daily_study_time_ms=result.daily_study_time_ms,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/vocabulary/profile", response_model=VocabularyProfileResponse)
async def get_vocabulary_profile(
    current_user: CurrentUser,
    db: Database,
) -> VocabularyProfile:
    connection = await db.scalar(
        select(MaimemoConnection).where(MaimemoConnection.user_id == current_user.id)
    )
    profile = None
    if connection is not None:
        profile = await db.scalar(
            select(VocabularyProfile)
            .join(
                MaimemoSyncSnapshot,
                MaimemoSyncSnapshot.id == VocabularyProfile.snapshot_id,
            )
            .where(
                VocabularyProfile.user_id == current_user.id,
                MaimemoSyncSnapshot.provider == connection.provider,
            )
            .order_by(VocabularyProfile.created_at.desc())
            .limit(1)
        )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vocabulary profile is available",
        )
    return profile
