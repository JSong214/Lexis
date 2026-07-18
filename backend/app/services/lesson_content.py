from uuid import UUID

from pydantic import ValidationError

from app.schemas.lesson import (
    ContextLessonContent,
    Exercise,
    ExerciseType,
    GradingMode,
    LessonApiModel,
    WordAid,
)
from app.schemas.topic import KnowledgeClaim, KnowledgeSource, TopicWordUsage

LEGACY_CONTEXT_LESSON_SCHEMA_VERSION = "context-lesson-v1"
LEGACY_CONTEXT_LESSON_KEYS = frozenset(
    {
        "title",
        "readingText",
        "unfamiliarWords",
        "targetWords",
        "grammarAnalysis",
        "exercises",
    }
)



class LegacyExercise(LessonApiModel):
    type: ExerciseType
    question: str
    options: list[str]
    expected_answer: str
    explanation_zh: str
    source_reference: str | None = None
    target_word: str | None = None
    skill: str | None = None
    grading_mode: GradingMode | None = None
    rubric: list[str] | None = None


class LegacyContextLessonContent(LessonApiModel):
    title: str
    reading_text: str
    unfamiliar_words: list[WordAid]
    target_words: list[str]
    grammar_analysis: list[str]
    exercises: list[LegacyExercise]


def upgrade_legacy_exercise(exercise: LegacyExercise, index: int) -> Exercise:
    return Exercise(
        type=exercise.type,
        question=exercise.question,
        options=exercise.options,
        expected_answer=exercise.expected_answer,
        source_reference=exercise.source_reference or f"Legacy exercise {index + 1}",
        target_word=exercise.target_word,
        skill=exercise.skill or exercise.type,
        grading_mode=exercise.grading_mode
        or ("exact_match" if exercise.options else "rubric"),
        rubric=exercise.rubric
        or ["Answer the question accurately using the lesson context."],
        explanation_zh=exercise.explanation_zh,
    )


def is_legacy_context_lesson(
    generation_metadata: dict[str, object],
    content: dict[str, object],
) -> bool:
    schema_version = generation_metadata.get("schema_version")
    return schema_version == LEGACY_CONTEXT_LESSON_SCHEMA_VERSION or (
        schema_version is None and frozenset(content) == LEGACY_CONTEXT_LESSON_KEYS
    )


def load_context_lesson_content(
    content: dict[str, object],
    *,
    lesson_id: UUID,
    generation_metadata: dict[str, object],
) -> ContextLessonContent:
    try:
        return ContextLessonContent.model_validate(content)
    except ValidationError:
        if not is_legacy_context_lesson(generation_metadata, content):
            raise

    legacy = LegacyContextLessonContent.model_validate(content)
    source_id = f"legacy-lesson-{lesson_id}"
    return ContextLessonContent(
        topic_id=f"legacy-{lesson_id}",
        title=legacy.title,
        content_mode="explanatory_scenario",
        core_question=f"What is the main idea of {legacy.title}?",
        reading_text=legacy.reading_text,
        word_usages=[TopicWordUsage(word=word, role="anchor") for word in legacy.target_words],
        knowledge_takeaway=(
            "This legacy lesson does not include structured knowledge metadata."
        ),
        knowledge_sources=[
            KnowledgeSource(
                id=source_id,
                title="Legacy lesson metadata",
                publisher="Lexis",
                url="about:blank",
                version=LEGACY_CONTEXT_LESSON_SCHEMA_VERSION,
            )
        ],
        knowledge_claims=[
            KnowledgeClaim(
                fact_id=f"{source_id}-content",
                source_ids=[source_id],
            )
        ],
        unfamiliar_words=legacy.unfamiliar_words,
        target_words=legacy.target_words,
        grammar_analysis=legacy.grammar_analysis,
        exercises=[
            upgrade_legacy_exercise(exercise, index)
            for index, exercise in enumerate(legacy.exercises)
        ],
    )
