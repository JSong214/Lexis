from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    MaimemoConnection,
    MaimemoSyncSnapshot,
    VocabularyProfile,
    VocabularySnapshotWord,
)
from app.services.vocabulary_context import VocabularyWordRecord


def _profile_word_records(profile: VocabularyProfile) -> list[VocabularyWordRecord]:
    return [
        VocabularyWordRecord(word=word, source_category=source_category)
        for source_category, words in (
            ("new", profile.new_words),
            ("fuzzy", profile.fuzzy_words),
            ("practice", profile.practice_words),
            ("mastered_sample", profile.mastered_words_sample),
        )
        for word in words
    ]


async def load_latest_vocabulary_inputs(
    db: AsyncSession,
    user_id: UUID,
) -> tuple[VocabularyProfile, MaimemoSyncSnapshot, list[VocabularyWordRecord]]:
    connection = await db.scalar(
        select(MaimemoConnection).where(MaimemoConnection.user_id == user_id)
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
                VocabularyProfile.user_id == user_id,
                MaimemoSyncSnapshot.provider == connection.provider,
            )
            .order_by(VocabularyProfile.created_at.desc())
            .limit(1)
        )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sync vocabulary before planning a lesson",
        )
    snapshot = await db.get(MaimemoSyncSnapshot, profile.snapshot_id)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Snapshot is unavailable",
        )

    rows = list(
        await db.scalars(
            select(VocabularySnapshotWord)
            .where(
                VocabularySnapshotWord.user_id == user_id,
                VocabularySnapshotWord.snapshot_id == snapshot.id,
            )
            .order_by(
                VocabularySnapshotWord.source_category,
                VocabularySnapshotWord.word,
            )
        )
    )
    words = [
        VocabularyWordRecord(word=row.word, source_category=row.source_category)
        for row in rows
    ]
    return profile, snapshot, words or _profile_word_records(profile)
