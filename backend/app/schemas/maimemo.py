import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


def to_camel(value: str) -> str:
    first, *rest = value.split("_")
    return first + "".join(part.capitalize() for part in rest)


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )


class ConnectionUpdate(BaseModel):
    provider: Literal["mock", "maimemo"] = "maimemo"
    secret: str | None = Field(default=None, max_length=4096)


class ConnectionResponse(ApiModel):
    configured: bool
    provider: str | None
    secret_saved: bool
    updated_at: datetime | None


class VocabularySnapshotWordResponse(ApiModel):
    word: str
    source_category: Literal["new", "fuzzy", "practice", "mastered_sample"]


class VocabularyProfileResponse(ApiModel):
    id: uuid.UUID
    snapshot_id: uuid.UUID
    new_words: list[str]
    fuzzy_words: list[str]
    practice_words: list[str]
    mastered_words_sample: list[str]
    tracked_word_count: int
    daily_finished_count: int
    daily_total_count: int
    daily_study_time_ms: int
    created_at: datetime
    snapshot_words: list[VocabularySnapshotWordResponse] = Field(default_factory=list)
