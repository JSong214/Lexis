import asyncio

from app.providers.llm import LessonGenerationContext, MockLLMProvider
from app.schemas.lesson import WordAid
from app.services.lesson_generation import (
    MAX_GENERATION_ATTEMPTS,
    LessonGenerationService,
    normalize_generated_content,
)
from app.services.lesson_validation import validate_context_lesson


class SequenceLessonProvider:
    name = "sequence"

    def __init__(self, responses):
        self.responses = list(responses)
        self.contexts = []

    async def generate_lesson(self, context):
        self.contexts.append(context)
        return self.responses.pop(0)


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
    assert result.metadata["prompt_version"] == "knowledge-lesson-generation-v1"
    assert result.metadata["schema_version"] == "context-lesson-v2"
    assert isinstance(result.metadata["latency_ms"], int)
    assert result.metadata["latency_ms"] >= 0
    assert result.metadata["input_tokens"] is None
    assert result.metadata["output_tokens"] is None
    assert result.metadata["retry_count"] == 0
    assert result.metadata["validation_results"] == []


def test_lesson_generation_retries_with_validation_errors() -> None:
    context = LessonGenerationContext(
        cefr_level="B2",
        exam_goal="General English",
        selected_words=["anchor"],
        mastered_words_sample=["stable"],
        tracked_word_count=3400,
    )
    valid_content = asyncio.run(MockLLMProvider().generate_lesson(context))
    invalid_content = valid_content.model_copy(
        update={"reading_text": f"{valid_content.reading_text} " + "extra " * 100}
    )
    provider = SequenceLessonProvider([invalid_content, valid_content])

    result = asyncio.run(LessonGenerationService(provider).generate(context))

    expected_errors = validate_context_lesson(
        invalid_content,
        "B2",
        required_target_words=["anchor"],
    )
    assert result.content == valid_content
    assert result.metadata["retry_count"] == 1
    assert len(provider.contexts) == 2
    assert provider.contexts[1].previous_validation_errors == tuple(expected_errors)


def test_lesson_generation_stops_after_three_total_attempts() -> None:
    context = LessonGenerationContext(
        cefr_level="B2",
        exam_goal="General English",
        selected_words=["anchor"],
        mastered_words_sample=["stable"],
        tracked_word_count=3400,
    )
    valid_content = asyncio.run(MockLLMProvider().generate_lesson(context))
    invalid_content = valid_content.model_copy(
        update={"reading_text": f"{valid_content.reading_text} " + "extra " * 100}
    )
    provider = SequenceLessonProvider([invalid_content] * MAX_GENERATION_ATTEMPTS)

    result = asyncio.run(LessonGenerationService(provider).generate(context))

    assert result.content == invalid_content
    assert result.metadata["retry_count"] == MAX_GENERATION_ATTEMPTS - 1
    assert len(provider.contexts) == MAX_GENERATION_ATTEMPTS
    assert all(provider.contexts[index].previous_validation_errors for index in (1, 2))


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
                "grading_mode": ("rubric" if exercise.type != "output" else "exact_match"),
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

    assert (
        validate_context_lesson(
            repaired_content,
            "B2",
            required_target_words=["anchor"],
        )
        == []
    )
