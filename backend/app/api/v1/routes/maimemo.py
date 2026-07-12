from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.core.secret_cipher import SecretCipher, get_secret_cipher
from app.db.session import get_db
from app.models import MaimemoConnection, MaimemoSyncSnapshot, VocabularyProfile
from app.providers.maimemo import MaimemoSyncProvider, get_maimemo_sync_provider
from app.schemas.maimemo import (
    ConnectionResponse,
    ConnectionUpdate,
    VocabularyProfileResponse,
)

router = APIRouter()
Database = Annotated[AsyncSession, Depends(get_db)]
Cipher = Annotated[SecretCipher | None, Depends(get_secret_cipher)]
SyncProvider = Annotated[MaimemoSyncProvider, Depends(get_maimemo_sync_provider)]


def connection_response(connection: MaimemoConnection | None) -> ConnectionResponse:
    if connection is None:
        return ConnectionResponse(
            configured=False,
            provider=None,
            secret_saved=False,
            updated_at=None,
        )
    return ConnectionResponse(
        configured=True,
        provider=connection.provider,
        secret_saved=connection.encrypted_secret is not None,
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
    provider: SyncProvider,
) -> VocabularyProfile:
    connection = await db.scalar(
        select(MaimemoConnection).where(MaimemoConnection.user_id == current_user.id)
    )
    if connection is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Configure Maimemo before syncing",
        )

    result = await provider.sync()
    snapshot = MaimemoSyncSnapshot(
        user_id=current_user.id,
        connection_id=connection.id,
        provider=connection.provider,
        new_words=result.new_words,
        fuzzy_words=result.fuzzy_words,
        mastered_words_sample=result.mastered_words_sample,
        mastered_word_count=result.mastered_word_count,
    )
    db.add(snapshot)
    await db.flush()
    profile = VocabularyProfile(
        user_id=current_user.id,
        snapshot_id=snapshot.id,
        new_words=result.new_words,
        fuzzy_words=result.fuzzy_words,
        mastered_words_sample=result.mastered_words_sample,
        mastered_word_count=result.mastered_word_count,
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
    profile = await db.scalar(
        select(VocabularyProfile)
        .where(VocabularyProfile.user_id == current_user.id)
        .order_by(VocabularyProfile.created_at.desc())
        .limit(1)
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vocabulary profile is available",
        )
    return profile
