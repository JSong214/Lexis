from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

TARGET_SOURCE_CATEGORIES = frozenset({"new", "fuzzy", "practice"})
PRIORITY_SOURCE_CATEGORIES = frozenset({"fuzzy", "practice"})
CONTEXT_SOURCE_CATEGORIES = frozenset({"mastered_sample"})


@dataclass(frozen=True)
class VocabularyWordRecord:
    word: str
    source_category: str


@dataclass(frozen=True)
class VocabularySelection:
    source_snapshot_id: UUID | None
    required_target_words: list[str]
    priority_words: list[str]
    context_words: list[str]
    excluded_words: list[str]


class VocabularySelectionError(ValueError):
    pass


def _unique_words(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        word = value.strip()
        normalized = word.casefold()
        if not word or normalized in seen:
            continue
        result.append(word)
        seen.add(normalized)
    return result


def build_vocabulary_selection(
    *,
    source_snapshot_id: UUID,
    words: Iterable[VocabularyWordRecord],
    requested_words: Iterable[str],
) -> VocabularySelection:
    records = [
        VocabularyWordRecord(word=word.word.strip(), source_category=word.source_category)
        for word in words
        if word.word.strip()
    ]
    word_by_key: dict[str, VocabularyWordRecord] = {}
    for record in records:
        word_by_key.setdefault(record.word.casefold(), record)

    requested = _unique_words(requested_words)
    if not requested:
        raise VocabularySelectionError("Select at least one target word")

    unknown_words = [
        word for word in requested if word.casefold() not in word_by_key
    ]
    if unknown_words:
        raise VocabularySelectionError(
            "Selected words must come from the latest vocabulary snapshot: "
            + ", ".join(unknown_words)
        )

    invalid_target_words = [
        word
        for word in requested
        if word_by_key[word.casefold()].source_category not in TARGET_SOURCE_CATEGORIES
    ]
    if invalid_target_words:
        raise VocabularySelectionError(
            "Mastered sample words are context-only and cannot be selected as targets: "
            + ", ".join(invalid_target_words)
        )

    required_keys = {word.casefold() for word in requested}
    priority_words = _unique_words(
        record.word
        for record in records
        if (
            record.source_category in PRIORITY_SOURCE_CATEGORIES
            and record.word.casefold() not in required_keys
        )
    )
    context_words = _unique_words(
        record.word
        for record in records
        if record.source_category in CONTEXT_SOURCE_CATEGORIES
    )
    return VocabularySelection(
        source_snapshot_id=source_snapshot_id,
        required_target_words=requested,
        priority_words=priority_words,
        context_words=context_words,
        excluded_words=[],
    )
