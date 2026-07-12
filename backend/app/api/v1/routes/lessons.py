from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.db.session import get_db
from app.models import (
    ContextLesson,
    ContextMasteryState,
    ExerciseFeedback,
    LessonAttempt,
    MaimemoSyncSnapshot,
    VocabularyProfile,
)
from app.providers.llm import (
    LessonGenerationContext,
    LLMProvider,
    LLMProviderConfigurationError,
    LLMProviderError,
    get_llm_provider,
)
from app.schemas.lesson import (
    ContextLessonContent,
    ContextLessonResponse,
    ExerciseAnswerRequest,
    ExerciseFeedbackResponse,
    LessonAttemptResponse,
    LessonCompletionResponse,
    LessonGenerationRequest,
    LessonHistoryItemResponse,
    MasteryUpdateResponse,
    PublicContextLessonContent,
    PublicExercise,
)
from app.services.lesson_validation import validate_context_lesson

router = APIRouter(prefix="/lessons")
Database = Annotated[AsyncSession, Depends(get_db)]
Provider = Annotated[LLMProvider, Depends(get_llm_provider)]


def provider_http_exception(error: LLMProviderError) -> HTTPException:
    return HTTPException(
        status_code=(
            status.HTTP_503_SERVICE_UNAVAILABLE
            if isinstance(error, LLMProviderConfigurationError)
            else status.HTTP_502_BAD_GATEWAY
        ),
        detail=str(error),
    )


def lesson_response(lesson: ContextLesson) -> ContextLessonResponse:
    content = ContextLessonContent.model_validate(lesson.content)
    return ContextLessonResponse(
        id=lesson.id,
        snapshot_id=lesson.snapshot_id,
        provider=lesson.provider,
        status=lesson.status,
        cefr_level=lesson.cefr_level,
        exam_goal=lesson.exam_goal,
        content=PublicContextLessonContent(
            title=content.title,
            reading_text=content.reading_text,
            unfamiliar_words=content.unfamiliar_words,
            target_words=content.target_words,
            grammar_analysis=content.grammar_analysis,
            exercises=[
                PublicExercise(
                    type=exercise.type,
                    question=exercise.question,
                    options=exercise.options,
                )
                for exercise in content.exercises
            ],
        ),
        validation_errors=lesson.validation_errors,
        created_at=lesson.created_at,
    )


def feedback_response(feedback: ExerciseFeedback) -> ExerciseFeedbackResponse:
    return ExerciseFeedbackResponse(
        id=feedback.id,
        attempt_id=feedback.attempt_id,
        exercise_index=feedback.exercise_index,
        exercise_type=feedback.exercise_type,
        answer=feedback.answer,
        is_correct=feedback.is_correct,
        feedback_text=feedback.feedback_text,
        updated_at=feedback.updated_at,
    )


async def get_owned_lesson(
    lesson_id: UUID,
    current_user: CurrentUser,
    db: Database,
) -> ContextLesson:
    lesson = await db.scalar(
        select(ContextLesson).where(
            ContextLesson.id == lesson_id,
            ContextLesson.user_id == current_user.id,
            ContextLesson.status == "valid",
        )
    )
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return lesson


async def attempt_response(
    attempt: LessonAttempt,
    db: Database,
) -> LessonAttemptResponse:
    feedback_items = (
        await db.scalars(
            select(ExerciseFeedback)
            .where(
                ExerciseFeedback.attempt_id == attempt.id,
                ExerciseFeedback.user_id == attempt.user_id,
            )
            .order_by(ExerciseFeedback.exercise_index)
        )
    ).all()
    return LessonAttemptResponse(
        id=attempt.id,
        lesson_id=attempt.lesson_id,
        status=attempt.status,
        final_summary=attempt.final_summary,
        completed_at=attempt.completed_at,
        feedback=[feedback_response(item) for item in feedback_items],
        created_at=attempt.created_at,
        updated_at=attempt.updated_at,
    )


@router.post("/generate", response_model=ContextLessonResponse)
async def generate_lesson(
    payload: LessonGenerationRequest,
    current_user: CurrentUser,
    db: Database,
    provider: Provider,
) -> ContextLessonResponse:
    profile = await db.scalar(
        select(VocabularyProfile)
        .where(VocabularyProfile.user_id == current_user.id)
        .order_by(VocabularyProfile.created_at.desc())
        .limit(1)
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sync vocabulary before generating a lesson",
        )
    snapshot = await db.get(MaimemoSyncSnapshot, profile.snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Snapshot is unavailable")

    available_words = {
        *profile.new_words,
        *profile.fuzzy_words,
        *profile.mastered_words_sample,
    }
    selected_words = (
        payload.selected_words
        or [
            *profile.new_words,
            *profile.fuzzy_words,
        ][:8]
    )
    if not selected_words or not set(selected_words).issubset(available_words):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Selected words must come from the latest vocabulary profile",
        )

    try:
        content = await provider.generate_lesson(
            LessonGenerationContext(
                cefr_level=payload.cefr_level,
                exam_goal=payload.exam_goal,
                selected_words=selected_words,
                mastered_words_sample=profile.mastered_words_sample,
                mastered_word_count=profile.mastered_word_count,
            )
        )
    except LLMProviderError as error:
        raise provider_http_exception(error) from error
    validation_errors = validate_context_lesson(content, payload.cefr_level)
    lesson = ContextLesson(
        user_id=current_user.id,
        snapshot_id=snapshot.id,
        provider=provider.name,
        status="valid" if not validation_errors else "invalid",
        cefr_level=payload.cefr_level,
        exam_goal=payload.exam_goal,
        content=content.model_dump(mode="json", by_alias=True),
        validation_errors=validation_errors,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    if validation_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Generated lesson failed validation", "errors": validation_errors},
        )
    return lesson_response(lesson)


@router.get("/{lesson_id}", response_model=ContextLessonResponse)
async def get_lesson(
    lesson_id: UUID,
    current_user: CurrentUser,
    db: Database,
) -> ContextLessonResponse:
    return lesson_response(await get_owned_lesson(lesson_id, current_user, db))


@router.get("/{lesson_id}/attempt", response_model=LessonAttemptResponse | None)
async def get_lesson_attempt(
    lesson_id: UUID,
    current_user: CurrentUser,
    db: Database,
) -> LessonAttemptResponse | None:
    await get_owned_lesson(lesson_id, current_user, db)
    attempt = await db.scalar(
        select(LessonAttempt).where(
            LessonAttempt.lesson_id == lesson_id,
            LessonAttempt.user_id == current_user.id,
        )
    )
    if attempt is None:
        return None
    return await attempt_response(attempt, db)


@router.post(
    "/{lesson_id}/answers",
    response_model=ExerciseFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_exercise_answer(
    lesson_id: UUID,
    payload: ExerciseAnswerRequest,
    current_user: CurrentUser,
    db: Database,
    provider: Provider,
) -> ExerciseFeedbackResponse:
    lesson = await get_owned_lesson(lesson_id, current_user, db)
    content = ContextLessonContent.model_validate(lesson.content)
    if payload.exercise_index >= len(content.exercises):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Exercise index is outside this lesson",
        )

    exercise = content.exercises[payload.exercise_index]
    try:
        evaluation = await provider.evaluate_exercise(
            exercise,
            payload.answer,
            content.target_words,
        )
    except LLMProviderError as error:
        raise provider_http_exception(error) from error
    attempt = await db.scalar(
        select(LessonAttempt).where(
            LessonAttempt.lesson_id == lesson.id,
            LessonAttempt.user_id == current_user.id,
        )
    )
    now = datetime.now(UTC)
    if attempt is None:
        attempt = LessonAttempt(
            user_id=current_user.id,
            lesson_id=lesson.id,
            status="draft",
            updated_at=now,
        )
        db.add(attempt)
        await db.flush()

    feedback = await db.scalar(
        select(ExerciseFeedback).where(
            ExerciseFeedback.attempt_id == attempt.id,
            ExerciseFeedback.exercise_index == payload.exercise_index,
            ExerciseFeedback.user_id == current_user.id,
        )
    )
    if feedback is None:
        feedback = ExerciseFeedback(
            attempt_id=attempt.id,
            user_id=current_user.id,
            exercise_index=payload.exercise_index,
            exercise_type=exercise.type,
            answer=payload.answer.strip(),
            is_correct=evaluation.is_correct,
            feedback_text=evaluation.feedback_text,
            updated_at=now,
        )
        db.add(feedback)
    else:
        feedback.answer = payload.answer.strip()
        feedback.is_correct = evaluation.is_correct
        feedback.feedback_text = evaluation.feedback_text
        feedback.updated_at = now
    attempt.updated_at = now

    await db.commit()
    await db.refresh(feedback)
    return feedback_response(feedback)


@router.post("/{lesson_id}/complete", response_model=LessonCompletionResponse)
async def complete_lesson(
    lesson_id: UUID,
    current_user: CurrentUser,
    db: Database,
    provider: Provider,
) -> LessonCompletionResponse:
    lesson = await get_owned_lesson(lesson_id, current_user, db)
    content = ContextLessonContent.model_validate(lesson.content)
    attempt = await db.scalar(
        select(LessonAttempt).where(
            LessonAttempt.lesson_id == lesson.id,
            LessonAttempt.user_id == current_user.id,
        )
    )
    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Answer every exercise before completing the lesson",
        )

    feedback_items = (
        await db.scalars(
            select(ExerciseFeedback)
            .where(
                ExerciseFeedback.attempt_id == attempt.id,
                ExerciseFeedback.user_id == current_user.id,
            )
            .order_by(ExerciseFeedback.exercise_index)
        )
    ).all()
    if len(feedback_items) != len(content.exercises):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Answer every exercise before completing the lesson",
        )

    mastery_states: list[ContextMasteryState] = []
    if attempt.status != "completed":
        correct_count = sum(item.is_correct for item in feedback_items)
        attempt.status = "completed"
        try:
            attempt.final_summary = await provider.summarize_attempt(
                correct_count,
                len(feedback_items),
                content.target_words,
            )
        except LLMProviderError as error:
            raise provider_http_exception(error) from error
        attempt.completed_at = datetime.now(UTC)
        attempt.updated_at = attempt.completed_at
        successful_lesson = correct_count / len(feedback_items) >= 0.75

        for word in content.target_words:
            mastery = await db.scalar(
                select(ContextMasteryState).where(
                    ContextMasteryState.user_id == current_user.id,
                    ContextMasteryState.word == word,
                )
            )
            if mastery is None:
                mastery = ContextMasteryState(
                    user_id=current_user.id,
                    word=word,
                    status="practicing",
                    exposure_count=0,
                    successful_attempts=0,
                    last_lesson_id=lesson.id,
                )
                db.add(mastery)
            mastery.exposure_count += 1
            if successful_lesson:
                mastery.successful_attempts += 1
            mastery.status = "stable" if mastery.successful_attempts >= 2 else "practicing"
            mastery.last_lesson_id = lesson.id
            mastery.updated_at = attempt.completed_at
            mastery_states.append(mastery)

        await db.commit()
        await db.refresh(attempt)
        for mastery in mastery_states:
            await db.refresh(mastery)
    else:
        mastery_states = list(
            (
                await db.scalars(
                    select(ContextMasteryState).where(
                        ContextMasteryState.user_id == current_user.id,
                        ContextMasteryState.word.in_(content.target_words),
                    )
                )
            ).all()
        )

    return LessonCompletionResponse(
        attempt=await attempt_response(attempt, db),
        mastery_updates=[
            MasteryUpdateResponse(
                word=mastery.word,
                status=mastery.status,
                exposure_count=mastery.exposure_count,
                successful_attempts=mastery.successful_attempts,
            )
            for mastery in sorted(
                mastery_states, key=lambda item: content.target_words.index(item.word)
            )
        ],
    )


@router.get("/{lesson_id}/completion", response_model=LessonCompletionResponse)
async def get_lesson_completion(
    lesson_id: UUID,
    current_user: CurrentUser,
    db: Database,
) -> LessonCompletionResponse:
    lesson = await get_owned_lesson(lesson_id, current_user, db)
    attempt = await db.scalar(
        select(LessonAttempt).where(
            LessonAttempt.lesson_id == lesson.id,
            LessonAttempt.user_id == current_user.id,
            LessonAttempt.status == "completed",
        )
    )
    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lesson is not complete",
        )

    content = ContextLessonContent.model_validate(lesson.content)
    mastery_states = list(
        (
            await db.scalars(
                select(ContextMasteryState).where(
                    ContextMasteryState.user_id == current_user.id,
                    ContextMasteryState.word.in_(content.target_words),
                )
            )
        ).all()
    )
    return LessonCompletionResponse(
        attempt=await attempt_response(attempt, db),
        mastery_updates=[
            MasteryUpdateResponse(
                word=mastery.word,
                status=mastery.status,
                exposure_count=mastery.exposure_count,
                successful_attempts=mastery.successful_attempts,
            )
            for mastery in sorted(
                mastery_states,
                key=lambda item: content.target_words.index(item.word),
            )
        ],
    )


@router.get("", response_model=list[LessonHistoryItemResponse])
async def list_lesson_history(
    current_user: CurrentUser,
    db: Database,
) -> list[LessonHistoryItemResponse]:
    lessons = (
        await db.scalars(
            select(ContextLesson)
            .where(
                ContextLesson.user_id == current_user.id,
                ContextLesson.status == "valid",
            )
            .order_by(ContextLesson.created_at.desc())
        )
    ).all()
    history: list[LessonHistoryItemResponse] = []
    for lesson in lessons:
        content = ContextLessonContent.model_validate(lesson.content)
        attempt = await db.scalar(
            select(LessonAttempt).where(
                LessonAttempt.lesson_id == lesson.id,
                LessonAttempt.user_id == current_user.id,
            )
        )
        feedback_items: list[ExerciseFeedback] = []
        if attempt is not None:
            feedback_items = list(
                (
                    await db.scalars(
                        select(ExerciseFeedback).where(
                            ExerciseFeedback.attempt_id == attempt.id,
                            ExerciseFeedback.user_id == current_user.id,
                        )
                    )
                ).all()
            )
        history.append(
            LessonHistoryItemResponse(
                id=lesson.id,
                title=content.title,
                cefr_level=lesson.cefr_level,
                attempt_status=attempt.status if attempt else None,
                answered_count=len(feedback_items),
                correct_count=sum(item.is_correct for item in feedback_items),
                exercise_count=len(content.exercises),
                created_at=lesson.created_at,
                completed_at=attempt.completed_at if attempt else None,
            )
        )
    return history
