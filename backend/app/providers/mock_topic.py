import re

from app.schemas.lesson import CefrLevel
from app.schemas.topic import (
    DynamicTopicCandidate,
    DynamicTopicPlan,
    RelationEvidence,
    TopicWordUsage,
    WordSemanticProfile,
    WordSense,
)


def _unique_words(words: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in words:
        word = value.strip()
        key = word.casefold()
        if not word or key in seen:
            continue
        seen.add(key)
        result.append(word)
    return result


def _sense_id(word: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", word.casefold()).strip("-") or "word"
    return f"mock.{slug}.contextual-usage"


def build_mock_dynamic_topic_plan(
    selected_words: list[str],
    cefr_level: CefrLevel,
) -> DynamicTopicPlan:
    words = _unique_words(selected_words)
    profiles = [
        WordSemanticProfile(
            word=word,
            lemma=word.casefold(),
            difficulty=cefr_level,
            senses=[
                WordSense(
                    id=_sense_id(word),
                    definition=(
                        f"The common contextual use of {word}, identified from its sentence "
                        "role and nearby words."
                    ),
                    meaning_zh=f"{word} 在具体语境中的常见含义",
                    part_of_speech="context-dependent",
                    collocations=[],
                    register="neutral",
                    semantic_domains=["language-use"],
                )
            ],
            source_name="mock-structured-lexical-analysis",
            source_version="v1",
        )
        for word in words
    ]

    focuses = words[:3]
    if len(focuses) == 1:
        focuses = [focuses[0], focuses[0]]
    modes = ["micro_case", "comparison", "explanatory_scenario"]
    candidates: list[DynamicTopicCandidate] = []
    for index, focus in enumerate(focuses):
        sense_id = _sense_id(focus)
        candidates.append(
            DynamicTopicCandidate(
                title=f"How context clarifies '{focus}'",
                core_question=(
                    f"How can a reader identify the intended use of '{focus}' in a sentence?"
                ),
                core_knowledge=(
                    "Sentence role, nearby words, and the surrounding situation help a reader "
                    "choose the intended meaning instead of treating a word in isolation."
                ),
                content_mode=modes[index],
                word_usages=[
                    TopicWordUsage(
                        word=word,
                        role="anchor" if word == focus else "deferred",
                        sense_id=sense_id if word == focus else None,
                        meaning_zh=(
                            f"{word} 在具体语境中的常见含义" if word == focus else None
                        ),
                        part_of_speech="context-dependent" if word == focus else None,
                        topic_role="the language form being interpreted" if word == focus else None,
                        relation_type="contextual-interpretation" if word == focus else None,
                    )
                    for word in words
                ],
                relation_evidence=[
                    RelationEvidence(
                        word=focus,
                        sense_id=sense_id,
                        topic_role="the language form being interpreted",
                        relation_type="contextual-interpretation",
                        explanation=(
                            f"The lesson examines how sentence evidence identifies the use of "
                            f"'{focus}'."
                        ),
                    )
                ],
                relation_explanation=(
                    f"'{focus}' is the Anchor word. Other selected words are Deferred rather "
                    "than forced into an unrelated lesson."
                ),
                rationale="One clear lexical question keeps the language lesson coherent.",
                core_fact=(
                    f"Readers can identify how '{focus}' is being used by checking its sentence "
                    "role and nearby words."
                ),
                supporting_facts=[
                    "A word should not be assigned a meaning without considering its context."
                ],
                causal_explanation=(
                    "Grammar and neighboring words narrow the plausible interpretation of the "
                    "Anchor word."
                ),
            )
        )
    return DynamicTopicPlan(profiles=profiles, candidates=candidates)
