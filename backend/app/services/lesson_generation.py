import re
from dataclasses import dataclass, replace
from time import perf_counter

from app.providers.llm import LessonGenerationContext, LLMProvider
from app.schemas.lesson import ContextLessonContent, Exercise
from app.services.lesson_validation import (
    EXPECTED_GRADING_MODES,
    contains_word,
    validate_context_lesson,
    validate_source_reference,
)

PROMPT_VERSION = "lesson-generation-v3"
SCHEMA_VERSION = "context-lesson-v1"
MAX_GENERATION_ATTEMPTS = 3
WORD_TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")


def _reading_sentences(reading_text: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+", reading_text.strip())


def _candidate_words(text: str) -> list[str]:
    return WORD_TOKEN_PATTERN.findall(text)


def _reference_for_word(word: str, sentences: list[str]) -> str | None:
    for index, sentence in enumerate(sentences, start=1):
        if contains_word(sentence, word):
            return f"reading:sentence-{index}:{word}"
    return None


def _reference_for_exercise(exercise: Exercise, sentences: list[str]) -> str:
    for text in (exercise.expected_answer, exercise.question):
        for candidate in _candidate_words(text):
            reference = _reference_for_word(candidate, sentences)
            if reference is not None:
                return reference
    for index, sentence in enumerate(sentences, start=1):
        candidates = _candidate_words(sentence)
        if candidates:
            return f"reading:sentence-{index}:{candidates[0]}"
    return "target_words"


def normalize_generated_content(content: ContextLessonContent) -> ContextLessonContent:
    """Repair deterministic lesson contract fields before semantic validation."""
    sentences = _reading_sentences(content.reading_text)
    normalized_exercises: list[Exercise] = []
    for exercise in content.exercises:
        source_reference = exercise.source_reference
        source_is_invalid = (
            validate_source_reference(source_reference, content.reading_text) is not None
        )
        if exercise.type == "output":
            source_reference = "target_words"
        elif exercise.type == "vocabulary_context" and exercise.target_word:
            if (
                source_is_invalid
                or exercise.target_word.casefold() not in source_reference.casefold()
            ):
                source_reference = _reference_for_word(
                    exercise.target_word, sentences
                ) or _reference_for_exercise(exercise, sentences)
        elif source_is_invalid:
            source_reference = _reference_for_exercise(exercise, sentences)

        expected_answer = exercise.expected_answer
        options = list(exercise.options)
        if (
            EXPECTED_GRADING_MODES[exercise.type] == "exact_match"
            and options
            and expected_answer not in options
        ):
            matching_option = next(
                (
                    option
                    for option in options
                    if option.strip().casefold() == expected_answer.strip().casefold()
                ),
                None,
            )
            expected_answer = matching_option or expected_answer
            if expected_answer not in options:
                options.append(expected_answer)

        updates: dict[str, object] = {
            "source_reference": source_reference,
            "grading_mode": EXPECTED_GRADING_MODES[exercise.type],
            "expected_answer": expected_answer,
            "options": options,
        }
        if exercise.type in {"syntax", "paragraph_logic"}:
            updates["target_word"] = None
        normalized_exercises.append(exercise.model_copy(update=updates))

    unfamiliar_words = [
        item
        for item in content.unfamiliar_words
        if contains_word(content.reading_text, item.word)
    ]
    return content.model_copy(
        update={"exercises": normalized_exercises, "unfamiliar_words": unfamiliar_words}
    )


@dataclass(frozen=True)
class GeneratedLesson:
    content: ContextLessonContent
    metadata: dict[str, object]


class LessonGenerationService:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    async def generate(self, context: LessonGenerationContext) -> GeneratedLesson:
        started_at = perf_counter()
        current_context = context
        retry_count = 0
        content: ContextLessonContent | None = None

        for attempt in range(MAX_GENERATION_ATTEMPTS):
            content = normalize_generated_content(
                await self.provider.generate_lesson(current_context)
            )
            validation_errors = validate_context_lesson(
                content,
                context.cefr_level,
                required_target_words=context.selection.required_target_words,
                priority_words=context.selection.priority_words,
            )
            if not validation_errors:
                break
            if attempt == MAX_GENERATION_ATTEMPTS - 1:
                break

            retry_count += 1
            current_context = replace(
                context,
                previous_validation_errors=tuple(validation_errors),
            )

        assert content is not None
        elapsed_ms = round((perf_counter() - started_at) * 1000)
        model_name = getattr(self.provider, "model", None)
        if not isinstance(model_name, str) or not model_name:
            model_name = getattr(self.provider, "model_name", None)
        if not isinstance(model_name, str) or not model_name:
            model_name = self.provider.name

        return GeneratedLesson(
            content=content,
            metadata={
                "provider": self.provider.name,
                "model": model_name,
                "prompt_version": PROMPT_VERSION,
                "schema_version": SCHEMA_VERSION,
                "latency_ms": elapsed_ms,
                "input_tokens": None,
                "output_tokens": None,
                "retry_count": retry_count,
            },
        )
