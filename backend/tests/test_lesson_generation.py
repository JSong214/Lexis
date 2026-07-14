import asyncio

from app.providers.llm import LessonGenerationContext, MockLLMProvider
from app.schemas.lesson import WordAid
from app.services.lesson_generation import (
    LessonGenerationService,
    normalize_generated_content,
)
from app.services.lesson_validation import validate_context_lesson


def test_lesson_generation_service_records_safe_metadata() -> None:
    result = asyncio.run(
        LessonGenerationService(MockLLMProvider()).generate(
            LessonGenerationContext(
                cefr_level="B2",
                exam_goal="General English",
                selected_words=["anchor"],
                mastered_words_sample=["stable"],
                tracked_word_count=3400,
            )
        )
    )

    assert result.content.target_words == ["anchor"]
    assert result.metadata["provider"] == "mock"
    assert result.metadata["model"] == "mock"
    assert result.metadata["prompt_version"] == "lesson-generation-v2"
    assert result.metadata["schema_version"] == "context-lesson-v1"
    assert isinstance(result.metadata["latency_ms"], int)
    assert result.metadata["latency_ms"] >= 0
    assert result.metadata["input_tokens"] is None
    assert result.metadata["output_tokens"] is None
    assert result.metadata["retry_count"] == 0


def test_normalize_generated_content_repairs_semantic_contract_fields() -> None:
    result = asyncio.run(
        LessonGenerationService(MockLLMProvider()).generate(
            LessonGenerationContext(
                cefr_level="B2",
                exam_goal="General English",
                selected_words=["anchor"],
                mastered_words_sample=["stable"],
                tracked_word_count=3400,
            )
        )
    )
    broken_exercises = [
        exercise.model_copy(
            update={
                "source_reference": "reading:paragraph-3",
                "grading_mode": (
                    "rubric" if exercise.type != "output" else "exact_match"
                ),
                "expected_answer": (
                    "model answer not listed"
                    if exercise.type in {"syntax", "paragraph_logic"}
                    else exercise.expected_answer
                ),
            }
        )
        for exercise in result.content.exercises
    ]
    broken_content = result.content.model_copy(
        update={
            "exercises": broken_exercises,
            "unfamiliar_words": [
                *result.content.unfamiliar_words,
                WordAid(word="not-in-reading", meaning_zh="无效"),
            ],
        }
    )

    repaired_content = normalize_generated_content(broken_content)

    assert validate_context_lesson(
        repaired_content,
        "B2",
        required_target_words=["anchor"],
    ) == []
