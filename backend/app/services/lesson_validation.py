import re

from app.schemas.lesson import CefrLevel, ContextLessonContent

CEFR_WORD_RANGES: dict[CefrLevel, tuple[int, int]] = {
    "A1": (50, 70),
    "A2": (70, 100),
    "B1": (100, 140),
    "B2": (140, 180),
    "C1": (160, 180),
    "C2": (160, 180),
}
REQUIRED_EXERCISE_TYPES = {
    "vocabulary_context",
    "syntax",
    "paragraph_logic",
    "output",
}
EXPECTED_GRADING_MODES = {
    "vocabulary_context": "exact_match",
    "syntax": "exact_match",
    "paragraph_logic": "exact_match",
    "output": "rubric",
}
VALID_SOURCE_PREFIXES = ("reading:", "target_words")
SOURCE_REFERENCE_PATTERN = re.compile(r"^reading:sentence-(?P<index>\d+):(?P<marker>.+)$")


def count_words(text: str) -> int:
    return len(text.split())


def contains_word(text: str, word: str) -> bool:
    return re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE) is not None
def validate_source_reference(source_reference: str, reading_text: str) -> str | None:
    if source_reference == "target_words":
        return None
    match = SOURCE_REFERENCE_PATTERN.fullmatch(source_reference)
    if match is None:
        return "has an invalid source reference"
    sentences = re.split(r"(?<=[.!?])\s+", reading_text.strip())
    sentence_index = int(match.group("index"))
    if sentence_index < 1 or sentence_index > len(sentences):
        return "references a missing reading sentence"
    marker_words = match.group("marker").replace("-", " ").split()
    if not all(
        contains_word(sentences[sentence_index - 1], word) for word in marker_words
    ):
        return "source evidence is missing from the referenced sentence"
    return None


def validate_context_lesson(
    content: ContextLessonContent,
    cefr_level: CefrLevel,
    *,
    required_target_words: list[str] | None = None,
    priority_words: list[str] | None = None,
) -> list[str]:
    del priority_words
    errors: list[str] = []
    minimum, maximum = CEFR_WORD_RANGES[cefr_level]
    word_count = count_words(content.reading_text)
    if not minimum <= word_count <= maximum:
        errors.append(f"Reading word count {word_count} is outside {minimum}-{maximum}")
    if len(content.unfamiliar_words) > 5:
        errors.append("Unfamiliar word count exceeds 5")
    if any(
        not item.word.strip() or not item.meaning_zh.strip()
        for item in content.unfamiliar_words
    ):
        errors.append("Unfamiliar words must include a word and Chinese meaning")
    missing_unfamiliar_words = [
        item.word
        for item in content.unfamiliar_words
        if not contains_word(content.reading_text, item.word)
    ]
    if missing_unfamiliar_words:
        errors.append(
            "Unfamiliar words missing from reading: " + ", ".join(missing_unfamiliar_words)
        )

    exercise_types = {exercise.type for exercise in content.exercises}
    if exercise_types != REQUIRED_EXERCISE_TYPES or len(content.exercises) != 4:
        errors.append("Lesson must contain exactly four required exercise types")
    if not content.grammar_analysis:
        errors.append("Grammar analysis is required")
    if not content.target_words:
        errors.append("At least one target word is required")

    target_word_keys = [word.strip().casefold() for word in content.target_words]
    if any(not word for word in target_word_keys):
        errors.append("Target words must not be empty")
    if len(target_word_keys) != len(set(target_word_keys)):
        errors.append("Target words must be unique")
    missing_target_words = [
        word
        for word, key in zip(content.target_words, target_word_keys, strict=True)
        if key and not contains_word(content.reading_text, word)
    ]
    if missing_target_words:
        errors.append("Target words missing from reading: " + ", ".join(missing_target_words))
    required_word_keys = {word.strip().casefold() for word in required_target_words or []}
    returned_word_keys = set(target_word_keys)
    missing_required_words = [
        word
        for word in required_target_words or []
        if word.strip().casefold() not in returned_word_keys
    ]
    if missing_required_words:
        errors.append("Required target words missing: " + ", ".join(missing_required_words))
    missing_required_in_reading = [
        word
        for word in required_target_words or []
        if not contains_word(content.reading_text, word)
    ]
    if missing_required_in_reading:
        errors.append(
            "Required target words missing from reading: "
            + ", ".join(missing_required_in_reading)
        )

    target_word_key_set = returned_word_keys | required_word_keys
    for exercise in content.exercises:
        source_error = validate_source_reference(
            exercise.source_reference,
            content.reading_text,
        )
        if source_error is not None:
            errors.append(f"Exercise {exercise.type} {source_error}")
        if (
            exercise.type == "vocabulary_context"
            and exercise.target_word is not None
            and exercise.target_word.casefold() not in exercise.source_reference.casefold()
        ):
            errors.append(f"Exercise {exercise.type} source must mention its target word")
        if exercise.skill.strip() == "":
            errors.append(f"Exercise {exercise.type} must declare a skill")
        expected_mode = EXPECTED_GRADING_MODES.get(exercise.type)
        if exercise.grading_mode != expected_mode:
            errors.append(f"Exercise {exercise.type} has an invalid grading mode")
        if (
            exercise.target_word is not None
            and exercise.target_word.strip().casefold() not in target_word_key_set
        ):
            errors.append(f"Exercise {exercise.type} references an unknown target word")
        if not exercise.rubric or any(not item.strip() for item in exercise.rubric):
            errors.append(f"Exercise {exercise.type} must declare a non-empty rubric")
        if exercise.grading_mode == "exact_match":
            if not exercise.expected_answer.strip():
                errors.append(f"Exercise {exercise.type} must declare an expected answer")
            if exercise.options and exercise.expected_answer not in exercise.options:
                errors.append(
                    f"Exercise {exercise.type} expected answer must be one of its options"
                )

    return errors
