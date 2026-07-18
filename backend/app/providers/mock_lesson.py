# ruff: noqa: E501

import re
from typing import TYPE_CHECKING

from app.schemas.lesson import ContextLessonContent, Exercise, WordAid
from app.schemas.topic import (
    KnowledgeBrief,
    KnowledgeClaim,
    KnowledgeFact,
    KnowledgeSource,
    TopicWordUsage,
)
from app.services.lesson_validation import CEFR_WORD_RANGES, contains_word

if TYPE_CHECKING:
    from app.providers.llm import LessonGenerationContext


def _default_brief() -> KnowledgeBrief:
    source = KnowledgeSource(
        id="lexis-mock-source",
        title="Lexis versioned mock knowledge fixture",
        publisher="Lexis",
        url="https://example.com/lexis/mock-knowledge",
        version="2026-07-17-v1",
    )
    return KnowledgeBrief(
        topic_id="mock-evidence-check",
        title="Checking an estimate with visible evidence",
        core_question="Why should a team show the evidence behind an estimate?",
        core_fact=KnowledgeFact(
            id="mock-core-fact",
            text="Visible evidence makes an estimate easier for another person to check.",
            source_ids=[source.id],
        ),
        supporting_facts=[],
        causal_explanation=(
            "Showing assumptions and criteria exposes the reasoning that produced the result."
        ),
        sources=[source],
        content_mode="explanatory_scenario",
    )


def _topic_sentences(brief: KnowledgeBrief) -> list[str]:
    if brief.topic_id == "anchoring-changes-estimates":
        return [
            "A project team must estimate a delivery date from ambiguous notes, so it writes clear criteria and tries to validate each assumption.",
            "Before discussion, the manager says sixty days, and that first number becomes an anchor for every later estimate.",
            "An initial numerical value can pull later estimates toward it, even when the number is weak evidence.",
            "The team notices that its answers stay close to sixty although different project records suggest a wider range.",
            "It hides the first number, studies three earlier projects, and asks each member to calculate an answer independently.",
            "The new estimates spread out because the members now begin with evidence instead of the manager's reference point.",
            "They compare the assumptions, explain the differences, and agree that no single rough number should end the discussion.",
            "The lesson is not that every first number is wrong, but that a starting point can quietly shape judgment.",
            "Visible criteria give the group another basis for revision, so the final range is easier to explain and check.",
        ]
    if brief.topic_id == "uncertainty-needs-a-range":
        return [
            "Two teams estimate the same delivery time, but one report is ambiguous while the other gives clear criteria for how to validate the result.",
            "The first report offers thirty days as a single anchor, while the second gives a range from twenty-six to thirty-six days.",
            "A measurement result is incomplete when it gives no quantitative statement of its uncertainty.",
            "The range does not mean that the team knows nothing; it shows which values the available evidence can reasonably support.",
            "Readers can see the central estimate and also judge how much variation remains around it.",
            "By contrast, one precise-looking number may hide different assumptions about suppliers, testing, and transport.",
            "The second team records those assumptions and explains what new evidence would narrow the range.",
            "This makes revision easier because a changed assumption can be connected to a changed result.",
            "A range is therefore useful when its method is visible, not because a range is automatically more accurate.",
        ]
    if brief.topic_id == "checkable-methods-build-trust":
        return [
            "A research team uses clear criteria to validate an estimate that was built from ambiguous records and an old result used as an anchor.",
            "Instead of publishing only the final number, the team shows each assumption, data source, and calculation step.",
            "Visible methods help other people evaluate whether a result is reliable and whether the same process can be repeated.",
            "A second team follows the recorded steps and discovers that one file used a different definition for the key measure.",
            "Because the method is explicit, the disagreement becomes a specific question rather than a general argument about trust.",
            "The researchers correct the definition, run the calculation again, and explain why the result changed.",
            "Showing a method does not prove that a conclusion is true, but it makes errors easier to locate and discuss.",
            "Readers can compare the evidence with the stated standards instead of accepting a confident conclusion without support.",
            "Trust grows from a checkable process, not merely from repeating the same answer.",
        ]
    if brief.topic_id.startswith("retrieval-"):
        return [
            "Maya does not only review a word list; she closes the page, tries to retain each meaning, and then checks her answer.",
            "She must apply one word in a new sentence, which helps reinforce access to the memory instead of repeating the printed example.",
            "Retrieval practice can produce more learning than spending the same time on additional study.",
            "The effort to recall an answer is useful even when the first attempt is incomplete.",
            "After checking feedback, Maya waits and tries the same idea in a different situation.",
            "The changed situation shows whether she remembers the meaning or only the original sentence.",
            "A short review still matters because it corrects mistakes before they become familiar.",
            "The important sequence is attempt, feedback, and another attempt rather than endless rereading.",
            "Over time, successful recall makes the knowledge easier to use when the book is closed.",
        ]
    return [
        "A project team makes an estimate, states its criteria, and keeps the evidence visible so another person can validate the reasoning.",
        "Visible evidence makes an estimate easier for another person to check.",
        "The team compares assumptions, explains differences, and revises the result when the evidence changes.",
        "This process does not guarantee a perfect answer, but it turns disagreement into questions that can be examined.",
        "Each person can identify the step that produced a different judgment.",
        "The final report preserves both the result and the reasons behind it.",
        "Later reviewers can apply the same criteria to new evidence instead of guessing how the answer was created.",
        "A checkable method makes uncertainty easier to discuss and revision easier to justify.",
    ]


def _language_sentences(brief: KnowledgeBrief, anchor_words: list[str]) -> list[str]:
    quoted_words = [f"'{word}'" for word in anchor_words]
    focus = (
        quoted_words[0]
        if len(quoted_words) == 1
        else ", ".join(quoted_words[:-1]) + " and " + quoted_words[-1]
    )
    return [
        f"A learner meets {focus} in a short message and pauses before choosing a meaning.",
        brief.core_fact.text,
        "The learner first checks the sentence role, then looks at the words immediately around the expression.",
        "A noun, verb, determiner, or adjective can create different expectations about how a word functions.",
        "Nearby examples also reveal whether the use is literal, grammatical, formal, or conversational.",
        "Instead of forcing every selected word into one sentence, the learner studies one clear use at a time.",
        "After identifying the use, the learner explains the clue and writes a new sentence with the same meaning.",
        "This small transfer check shows whether the learner understood the pattern rather than memorized one example.",
    ]


def _fit_reading(sentences: list[str], minimum: int, maximum: int) -> str:
    selected: list[str] = []
    index = 0
    while len(" ".join(selected).split()) < minimum:
        selected.append(sentences[index % len(sentences)])
        index += 1
    words = " ".join(selected).split()
    if len(words) > maximum:
        words = words[:maximum]
        return " ".join(words).rstrip(".,;:") + "."
    return " ".join(words)


def _sentence_number(reading_text: str, word: str) -> int | None:
    sentences = re.split(r"(?<=[.!?])\s+", reading_text.strip())
    return next(
        (
            index
            for index, sentence in enumerate(sentences, start=1)
            if contains_word(sentence, word)
        ),
        None,
    )


def _source_for(reading_text: str, word: str) -> str:
    sentence_number = _sentence_number(reading_text, word)
    return (
        f"reading:sentence-{sentence_number}:{word}"
        if sentence_number is not None
        else "target_words"
    )


def _source_for_fact(reading_text: str, fact_text: str) -> str:
    for word in re.findall(r"[A-Za-z]+", fact_text):
        if len(word) > 3 and contains_word(reading_text, word):
            return _source_for(reading_text, word)
    return _first_sentence_source(reading_text)


def _first_sentence_source(reading_text: str) -> str:
    first_sentence = re.split(r"(?<=[.!?])\s+", reading_text.strip())[0]
    marker = next(iter(re.findall(r"[A-Za-z]+", first_sentence)), "reading")
    return f"reading:sentence-1:{marker}"


def build_mock_lesson(context: "LessonGenerationContext") -> ContextLessonContent:
    brief = context.knowledge_brief or _default_brief()
    proposal = context.topic_proposal
    anchor_words = context.selection.anchor_words or context.selected_words[:3]
    if proposal is not None:
        word_usages = proposal.word_usages
    else:
        word_usages = [
            TopicWordUsage(
                word=word,
                role="anchor",
                sense_id=f"mock.{word.casefold()}",
                meaning_zh="目标词",
                part_of_speech="unknown",
                topic_role="mock lesson focus",
                relation_type="fixture-relation",
            )
            for word in anchor_words
        ]

    minimum, maximum = CEFR_WORD_RANGES[context.cefr_level]
    sentences = (
        _language_sentences(brief, anchor_words)
        if brief.topic_id.startswith("language-")
        else _topic_sentences(brief)
    )
    combined_sentences = " ".join(sentences)
    missing_anchor_words = [
        word for word in anchor_words if not contains_word(combined_sentences, word)
    ]
    if missing_anchor_words:
        sentences.insert(
            0,
            "The team examines " + ", ".join(missing_anchor_words) + " in one clear example.",
        )
    reading_text = _fit_reading(sentences, minimum, maximum)
    vocabulary_target = anchor_words[0] if anchor_words else "estimate"
    vocabulary_usage = next(
        (item for item in word_usages if item.word.casefold() == vocabulary_target.casefold()),
        None,
    )
    vocabulary_answer = (
        vocabulary_usage.meaning_zh
        if vocabulary_usage is not None and vocabulary_usage.meaning_zh
        else "the meaning shown by the reading context"
    )
    vocabulary_exercise = Exercise(
        type="vocabulary_context",
        question=f"What does {vocabulary_target} mean in this reading?",
        options=[vocabulary_answer, "a final answer that cannot change", "an unrelated detail"],
        expected_answer=vocabulary_answer,
        source_reference=_source_for(reading_text, vocabulary_target),
        target_word=vocabulary_target,
        skill="vocabulary_in_context",
        grading_mode="exact_match",
        rubric=[f"Identifies the selected sense of {vocabulary_target}."],
        explanation_zh=f"这里使用的是提案中为 {vocabulary_target} 选定的具体词义。",
    )
    syntax_exercise = Exercise(
        type="syntax",
        question="Why does the opening sentence use the present simple?",
        options=[
            "To describe a general process or repeated action",
            "To report an action in progress at this exact moment",
            "To place the action before another past event",
        ],
        expected_answer="To describe a general process or repeated action",
        source_reference=_first_sentence_source(reading_text),
        target_word=None,
        skill="syntax",
        grading_mode="exact_match",
        rubric=["Explains the general or repeated use of the present simple."],
        explanation_zh="一般现在时在这里用于说明普遍规律、重复行为或解释性过程。",
    )
    knowledge_exercise = Exercise(
        type="paragraph_logic",
        question=brief.core_question,
        options=[
            brief.core_fact.text,
            "Because a confident number never needs evidence.",
            "Because uncertainty disappears when it is not reported.",
        ],
        expected_answer=brief.core_fact.text,
        source_reference=_source_for_fact(reading_text, brief.core_fact.text),
        target_word=None,
        skill="knowledge_understanding",
        grading_mode="exact_match",
        rubric=["Selects the explanation supported by the KnowledgeBrief."],
        explanation_zh="这道题只检查核心知识理解，不要求使用目标词。",
    )
    output_exercise = Exercise(
        type="output",
        question=(
            f"Use {vocabulary_target} in a new situation while keeping the same core meaning."
        ),
        options=[],
        expected_answer=f"I use {vocabulary_target} in a new but related situation.",
        source_reference="target_words",
        target_word=vocabulary_target,
        skill="vocabulary_near_transfer",
        grading_mode="rubric",
        rubric=[
            f"Uses {vocabulary_target} with the selected core meaning.",
            "Applies the word to a new situation in a complete sentence.",
        ],
        explanation_zh="答案需要在新语境中自然使用指定 Anchor word，并保持相同核心词义。",
    )
    claims = [brief.core_fact, *brief.supporting_facts]
    return ContextLessonContent(
        topic_id=brief.topic_id,
        title=brief.title,
        content_mode=brief.content_mode,
        core_question=brief.core_question,
        reading_text=reading_text,
        word_usages=word_usages,
        knowledge_takeaway=brief.core_fact.text,
        knowledge_sources=brief.sources,
        knowledge_claims=[
            KnowledgeClaim(fact_id=fact.id, source_ids=fact.source_ids) for fact in claims
        ],
        unfamiliar_words=[
            WordAid(word="evidence", meaning_zh="证据"),
        ]
        if contains_word(reading_text, "evidence")
        else [],
        target_words=anchor_words,
        grammar_analysis=[
            "present simple：用于说明普遍规律、重复行为或解释性过程。",
            "when + clause：说明判断或行动发生的条件。",
        ],
        exercises=[
            vocabulary_exercise,
            syntax_exercise,
            knowledge_exercise,
            output_exercise,
        ],
    )
