from dataclasses import dataclass

from app.providers.llm import LessonGenerationContext
from app.schemas.lesson import CefrLevel


@dataclass(frozen=True)
class FixedLessonCase:
    name: str
    cefr_level: CefrLevel
    exam_goal: str
    selected_words: list[str]
    mastered_words_sample: list[str]


FIXED_LESSON_CASES = (
    FixedLessonCase(
        name="core_estimation",
        cefr_level="B2",
        exam_goal="IELTS reading",
        selected_words=["anchor", "estimate", "ambiguous"],
        mastered_words_sample=["stable", "pattern"],
    ),
    FixedLessonCase(
        name="practice_reinforcement",
        cefr_level="B1",
        exam_goal="General English",
        selected_words=["review", "reinforce", "apply"],
        mastered_words_sample=["stable", "contrast"],
    ),
)


def context_for(case: FixedLessonCase) -> LessonGenerationContext:
    return LessonGenerationContext(
        cefr_level=case.cefr_level,
        exam_goal=case.exam_goal,
        selected_words=case.selected_words,
        mastered_words_sample=case.mastered_words_sample,
        tracked_word_count=3400,
    )
