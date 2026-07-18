import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.maimemo import to_camel
from app.schemas.topic import (
    ContentMode,
    KnowledgeClaim,
    KnowledgeSource,
    TopicWordUsage,
)

CefrLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
ExerciseType = Literal[
    "vocabulary_context",
    "syntax",
    "paragraph_logic",
    "output",
]
GradingMode = Literal["exact_match", "rubric"]



class LessonApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )


class WordAid(LessonApiModel):
    word: str
    meaning_zh: str


class Exercise(LessonApiModel):
    type: ExerciseType
    question: str
    options: list[str]
    expected_answer: str
    source_reference: str = Field(min_length=1, max_length=200)
    target_word: str | None
    skill: str = Field(min_length=1, max_length=80)
    grading_mode: GradingMode
    rubric: list[str] = Field(min_length=1, max_length=5)
    explanation_zh: str


class ContextLessonContent(LessonApiModel):
    topic_id: str
    title: str
    content_mode: ContentMode
    core_question: str
    reading_text: str
    word_usages: list[TopicWordUsage]
    knowledge_takeaway: str
    knowledge_sources: list[KnowledgeSource] = Field(min_length=1)
    knowledge_claims: list[KnowledgeClaim] = Field(min_length=1, max_length=3)
    unfamiliar_words: list[WordAid]
    target_words: list[str]
    grammar_analysis: list[str]
    exercises: list[Exercise]


class PublicExercise(LessonApiModel):
    type: ExerciseType
    question: str
    options: list[str]


class PublicContextLessonContent(LessonApiModel):
    topic_id: str
    title: str
    content_mode: ContentMode
    core_question: str
    reading_text: str
    word_usages: list[TopicWordUsage]
    knowledge_takeaway: str
    knowledge_sources: list[KnowledgeSource]
    unfamiliar_words: list[WordAid]
    target_words: list[str]
    grammar_analysis: list[str]
    exercises: list[PublicExercise]


class LessonGenerationRequest(LessonApiModel):
    cefr_level: CefrLevel = "B2"
    exam_goal: str = Field(default="General English", max_length=120)
    selected_words: list[str] = Field(min_length=1, max_length=16)
    proposal_id: str = Field(min_length=1, max_length=120)
    anchor_words: list[str] = Field(min_length=1, max_length=5)


class ContextLessonResponse(LessonApiModel):
    id: uuid.UUID
    snapshot_id: uuid.UUID
    provider: str
    status: str
    cefr_level: CefrLevel
    exam_goal: str
    content: PublicContextLessonContent
    validation_errors: list[str]
    generation_metadata: dict[str, object]
    created_at: datetime


class ExerciseAnswerRequest(LessonApiModel):
    exercise_index: int = Field(ge=0)
    answer: str = Field(min_length=1, max_length=2000)


class ExerciseFeedbackResponse(LessonApiModel):
    id: uuid.UUID
    attempt_id: uuid.UUID
    exercise_index: int
    exercise_type: ExerciseType
    answer: str
    is_correct: bool
    feedback_text: str
    updated_at: datetime


class LessonAttemptResponse(LessonApiModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    status: str
    final_summary: str | None
    completed_at: datetime | None
    feedback: list[ExerciseFeedbackResponse]
    created_at: datetime
    updated_at: datetime


class MasteryUpdateResponse(LessonApiModel):
    word: str
    status: str
    exposure_count: int
    successful_attempts: int


class LessonCompletionResponse(LessonApiModel):
    attempt: LessonAttemptResponse
    mastery_updates: list[MasteryUpdateResponse]


class LessonHistoryItemResponse(LessonApiModel):
    id: uuid.UUID
    title: str
    cefr_level: CefrLevel
    attempt_status: str | None
    answered_count: int
    correct_count: int
    exercise_count: int
    created_at: datetime
    completed_at: datetime | None
