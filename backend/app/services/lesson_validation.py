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


def count_words(text: str) -> int:
    return len(text.split())


def validate_context_lesson(
    content: ContextLessonContent,
    cefr_level: CefrLevel,
) -> list[str]:
    errors: list[str] = []
    minimum, maximum = CEFR_WORD_RANGES[cefr_level]
    word_count = count_words(content.reading_text)
    if not minimum <= word_count <= maximum:
        errors.append(f"Reading word count {word_count} is outside {minimum}-{maximum}")
    if len(content.unfamiliar_words) > 5:
        errors.append("Unfamiliar word count exceeds 5")
    exercise_types = {exercise.type for exercise in content.exercises}
    if exercise_types != REQUIRED_EXERCISE_TYPES or len(content.exercises) != 4:
        errors.append("Lesson must contain exactly four required exercise types")
    if not content.grammar_analysis:
        errors.append("Grammar analysis is required")
    if not content.target_words:
        errors.append("At least one target word is required")
    return errors
