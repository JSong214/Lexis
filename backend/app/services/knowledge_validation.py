from app.schemas.lesson import CefrLevel, ContextLessonContent
from app.schemas.topic import KnowledgeBrief, TopicProposal

CEFR_ANCHOR_RANGES: dict[CefrLevel, tuple[int, int]] = {
    "A1": (2, 3),
    "A2": (2, 3),
    "B1": (3, 4),
    "B2": (3, 4),
    "C1": (4, 5),
    "C2": (4, 5),
}


def validate_knowledge_contract(
    content: ContextLessonContent,
    cefr_level: CefrLevel,
    *,
    topic_proposal: TopicProposal | None,
    knowledge_brief: KnowledgeBrief | None,
) -> list[str]:
    if topic_proposal is None and knowledge_brief is None:
        return []
    if topic_proposal is None or knowledge_brief is None:
        return ["TopicProposal and KnowledgeBrief must be validated together"]

    errors: list[str] = []
    if content.topic_id != topic_proposal.topic_id:
        errors.append("Lesson topic does not match the confirmed TopicProposal")
    if content.topic_id != knowledge_brief.topic_id:
        errors.append("Lesson topic does not match the KnowledgeBrief")
    if content.content_mode != topic_proposal.content_mode:
        errors.append("Lesson content mode does not match the TopicProposal")
    if content.content_mode != knowledge_brief.content_mode:
        errors.append("Lesson content mode does not match the KnowledgeBrief")
    if content.core_question.strip() != knowledge_brief.core_question.strip():
        errors.append("Lesson core question does not match the KnowledgeBrief")
    if not content.knowledge_takeaway.strip():
        errors.append("KnowledgeTakeaway is required")

    expected_anchor_usages = {
        usage.word.casefold(): usage
        for usage in topic_proposal.word_usages
        if usage.role == "anchor"
    }
    returned_anchor_usages = {
        usage.word.casefold(): usage
        for usage in content.word_usages
        if usage.role == "anchor"
    }
    target_word_keys = {word.casefold() for word in content.target_words}
    if target_word_keys != set(expected_anchor_usages):
        errors.append("targetWords must equal the confirmed Anchor words")
    if set(returned_anchor_usages) != set(expected_anchor_usages):
        errors.append("wordUsages must preserve the confirmed Anchor roles")

    recommended_minimum, maximum = CEFR_ANCHOR_RANGES[cefr_level]
    if not 1 <= len(expected_anchor_usages) <= maximum:
        errors.append(
            f"{cefr_level} allows 1-{maximum} Anchor words; "
            f"{recommended_minimum}-{maximum} is recommended; "
            f"received {len(expected_anchor_usages)}"
        )
    for key, expected in expected_anchor_usages.items():
        returned = returned_anchor_usages.get(key)
        if returned is not None and returned.sense_id != expected.sense_id:
            errors.append(f"Anchor word {expected.word} changed its selected sense")

    brief_source_ids = {source.id for source in knowledge_brief.sources}
    returned_source_ids = {source.id for source in content.knowledge_sources}
    if returned_source_ids != brief_source_ids:
        errors.append("Knowledge sources must exactly match the KnowledgeBrief")

    facts = {
        fact.id: fact
        for fact in [knowledge_brief.core_fact, *knowledge_brief.supporting_facts]
    }
    returned_fact_ids = {claim.fact_id for claim in content.knowledge_claims}
    if knowledge_brief.core_fact.id not in returned_fact_ids:
        errors.append("Knowledge claims must include the core KnowledgeBrief fact")
    for claim in content.knowledge_claims:
        fact = facts.get(claim.fact_id)
        if fact is None:
            errors.append(f"Knowledge claim {claim.fact_id} is outside the KnowledgeBrief")
            continue
        if not set(claim.source_ids) <= set(fact.source_ids):
            errors.append(
                f"Knowledge claim {claim.fact_id} references a source outside its fact mapping"
            )
    return errors
