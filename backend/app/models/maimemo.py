import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MaimemoConnection(Base):
    __tablename__ = "maimemo_connections"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(32), default="mock")
    encrypted_secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class MaimemoSyncSnapshot(Base):
    __tablename__ = "maimemo_sync_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    connection_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("maimemo_connections.id", ondelete="CASCADE"),
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="succeeded")
    new_words: Mapped[list[str]] = mapped_column(JSON)
    fuzzy_words: Mapped[list[str]] = mapped_column(JSON)
    practice_words: Mapped[list[str]] = mapped_column(JSON)
    mastered_words_sample: Mapped[list[str]] = mapped_column(JSON)
    tracked_word_count: Mapped[int] = mapped_column(Integer)
    daily_finished_count: Mapped[int] = mapped_column(Integer, default=0)
    daily_total_count: Mapped[int] = mapped_column(Integer, default=0)
    daily_study_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class VocabularyProfile(Base):
    __tablename__ = "vocabulary_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("maimemo_sync_snapshots.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    new_words: Mapped[list[str]] = mapped_column(JSON)
    fuzzy_words: Mapped[list[str]] = mapped_column(JSON)
    practice_words: Mapped[list[str]] = mapped_column(JSON)
    mastered_words_sample: Mapped[list[str]] = mapped_column(JSON)
    tracked_word_count: Mapped[int] = mapped_column(Integer)
    daily_finished_count: Mapped[int] = mapped_column(Integer, default=0)
    daily_total_count: Mapped[int] = mapped_column(Integer, default=0)
    daily_study_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
