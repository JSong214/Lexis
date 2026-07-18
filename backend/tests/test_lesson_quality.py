import asyncio

import pytest
from fixed_lesson_cases import FIXED_LESSON_CASES, context_for

from app.providers.llm import MockLLMProvider
from app.services.lesson_validation import validate_context_lesson


def generate_fixed_content(case):
    return asyncio.run(MockLLMProvider().generate_lesson(context_for(case)))


@pytest.mark.parametrize("case", FIXED_LESSON_CASES, ids=lambda case: case.name)
def test_fixed_lesson_cases_meet_quality_gate_and_use_targets(case) -> None:
    content = generate_fixed_content(case)

    assert (
        validate_context_lesson(
            content,
            case.cefr_level,
            required_target_words=case.selected_words,
        )
        == []
    )
    if case.name == "core_estimation":
        assert content.topic_id == "anchoring-changes-estimates"
        assert "first number becomes an anchor" in content.reading_text
    else:
        assert content.topic_id.startswith("retrieval-")
        assert "does not only review" in content.reading_text
        assert "apply one word" in content.reading_text
        assert "helps reinforce" in content.reading_text
    assert content.knowledge_takeaway
    assert content.knowledge_sources
    assert content.knowledge_claims
    assert "TODO" not in content.reading_text
    assert len(content.target_words) == len(
        {word.casefold() for word in content.target_words}
    )

    grading_modes = {
        "vocabulary_context": "exact_match",
        "syntax": "exact_match",
        "paragraph_logic": "exact_match",
        "output": "rubric",
    }
    target_word_keys = {word.casefold() for word in content.target_words}
    for exercise in content.exercises:
        assert exercise.source_reference.startswith(("reading:", "target_words"))
        assert exercise.skill
        assert exercise.rubric
        assert exercise.grading_mode == grading_modes[exercise.type]
        if exercise.target_word is not None:
            assert exercise.target_word.casefold() in target_word_keys


def test_fixed_feedback_cases_explain_correctness_and_next_step() -> None:
    case = FIXED_LESSON_CASES[0]
    content = generate_fixed_content(case)
    provider = MockLLMProvider()
    vocabulary_exercise = next(
        exercise for exercise in content.exercises if exercise.type == "vocabulary_context"
    )
    wrong_answer = next(
        option
        for option in vocabulary_exercise.options
        if option != vocabulary_exercise.expected_answer
    )

    correct = asyncio.run(
        provider.evaluate_exercise(
            vocabulary_exercise,
            vocabulary_exercise.expected_answer.upper(),
            content.target_words,
        )
    )
    incorrect = asyncio.run(
        provider.evaluate_exercise(
            vocabulary_exercise,
            wrong_answer,
            content.target_words,
        )
    )

    assert correct.is_correct is True
    assert correct.feedback_text.startswith("回答正确")
    assert vocabulary_exercise.explanation_zh in correct.feedback_text
    assert incorrect.is_correct is False
    assert incorrect.feedback_text.startswith("还不准确")
    assert vocabulary_exercise.explanation_zh in incorrect.feedback_text

    output_exercise = next(exercise for exercise in content.exercises if exercise.type == "output")
    output_correct = asyncio.run(
        provider.evaluate_exercise(
            output_exercise,
            f"I use {output_exercise.target_word} in a clear sentence.",
            content.target_words,
        )
    )
    output_incorrect = asyncio.run(
        provider.evaluate_exercise(
            output_exercise,
            "This sentence does not use the selected vocabulary.",
            content.target_words,
        )
    )

    fragment = asyncio.run(
        provider.evaluate_exercise(
            output_exercise,
            output_exercise.target_word or "",
            content.target_words,
        )
    )
    wrong_target = next(
        word for word in content.target_words if word != output_exercise.target_word
    )
    wrong_target_feedback = asyncio.run(
        provider.evaluate_exercise(
            output_exercise,
            f"I use {wrong_target} in a clear sentence.",
            content.target_words,
        )
    )

    assert output_correct.is_correct is True
    assert "目标词" in output_correct.feedback_text
    assert output_incorrect.is_correct is False
    assert "请使用指定目标词" in output_incorrect.feedback_text
    assert fragment.is_correct is False
    assert "至少四个词" in fragment.feedback_text
    assert wrong_target_feedback.is_correct is False
    assert "指定目标词" in wrong_target_feedback.feedback_text

    summary = asyncio.run(provider.summarize_attempt(3, 4, content.target_words))
    assert "4 道练习" in summary
    assert "3 道表现稳定" in summary
    assert content.target_words[0] in summary


def test_fixed_cases_use_distinct_scenarios() -> None:
    core_content = generate_fixed_content(FIXED_LESSON_CASES[0])
    practice_content = generate_fixed_content(FIXED_LESSON_CASES[1])

    assert core_content.title != practice_content.title
    assert core_content.reading_text != practice_content.reading_text
    assert "project team" in core_content.reading_text
    assert "Maya" in practice_content.reading_text


def test_fixed_quality_gate_rejects_untraceable_output() -> None:
    case = FIXED_LESSON_CASES[0]
    content = generate_fixed_content(case)

    missing_word_content = content.model_copy(
        update={"target_words": [*content.target_words, "missing"]}
    )
    missing_word_errors = validate_context_lesson(
        missing_word_content,
        case.cefr_level,
        required_target_words=case.selected_words,
    )
    assert any(
        error.startswith("Target words missing from reading:")
        and "missing" in error
        for error in missing_word_errors
    )

    broken_exercises = list(content.exercises)
    broken_exercises[0] = broken_exercises[0].model_copy(update={"grading_mode": "rubric"})
    broken_content = content.model_copy(update={"exercises": broken_exercises})
    broken_errors = validate_context_lesson(broken_content, case.cefr_level)
    assert "Exercise vocabulary_context has an invalid grading mode" in broken_errors

    source_exercises = list(content.exercises)
    source_exercises[1] = source_exercises[1].model_copy(
        update={"source_reference": "reading:paragraph-3"}
    )
    source_errors = validate_context_lesson(
        content.model_copy(update={"exercises": source_exercises}),
        case.cefr_level,
    )
    assert "Exercise syntax has an invalid source reference" in source_errors
