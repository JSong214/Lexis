from uuid import uuid4

import pytest

from app.services.vocabulary_context import (
    VocabularySelectionError,
    VocabularyWordRecord,
    build_vocabulary_selection,
)


def test_build_vocabulary_selection_separates_word_roles() -> None:
    snapshot_id = uuid4()
    selection = build_vocabulary_selection(
        source_snapshot_id=snapshot_id,
        words=[
            VocabularyWordRecord(word="anchor", source_category="new"),
            VocabularyWordRecord(word="retain", source_category="fuzzy"),
            VocabularyWordRecord(word="review", source_category="practice"),
            VocabularyWordRecord(word="stable", source_category="mastered_sample"),
        ],
        requested_words=["anchor"],
    )

    assert selection.source_snapshot_id == snapshot_id
    assert selection.required_target_words == ["anchor"]
    assert selection.priority_words == ["retain", "review"]
    assert selection.context_words == ["stable"]
    assert selection.excluded_words == []


def test_build_vocabulary_selection_rejects_unknown_words() -> None:
    with pytest.raises(VocabularySelectionError, match="latest vocabulary snapshot"):
        build_vocabulary_selection(
            source_snapshot_id=uuid4(),
            words=[VocabularyWordRecord(word="anchor", source_category="new")],
            requested_words=["missing"],
        )


def test_build_vocabulary_selection_rejects_mastered_words_as_targets() -> None:
    with pytest.raises(VocabularySelectionError, match="context-only"):
        build_vocabulary_selection(
            source_snapshot_id=uuid4(),
            words=[
                VocabularyWordRecord(word="stable", source_category="mastered_sample"),
            ],
            requested_words=["stable"],
        )
