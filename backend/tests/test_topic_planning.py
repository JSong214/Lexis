import asyncio
from uuid import uuid4

import pytest

from app.providers.knowledge import FixtureKnowledgeLibrary
from app.providers.lexical import FixtureLexicalSource
from app.providers.llm import LessonGenerationContext, MockLLMProvider
from app.schemas.topic import KnowledgeClaim
from app.services.lesson_validation import validate_context_lesson
from app.services.topic_planning import TopicPlanningError, TopicPlanningService
from app.services.vocabulary_context import VocabularySelection


def planning_service() -> TopicPlanningService:
    return TopicPlanningService(
        FixtureLexicalSource(),
        FixtureKnowledgeLibrary(),
    )


def test_topic_proposals_bind_senses_roles_and_relation_evidence() -> None:
    result = planning_service().propose(
        snapshot_id=uuid4(),
        selected_words=[
            "anchor",
            "estimate",
            "ambiguous",
            "criteria",
            "validate",
            "segment",
        ],
        cefr_level="B2",
    )

    assert len(result.proposals) == 3
    anchor_profile = next(profile for profile in result.profiles if profile.word == "anchor")
    assert {sense.id for sense in anchor_profile.senses} == {
        "anchor.reference_point",
        "anchor.secure_object",
    }
    for proposal in result.proposals:
        assert 3 <= len(proposal.anchor_words) <= 4
        evidence_words = {item.word for item in proposal.relation_evidence}
        assert set(proposal.anchor_words) <= evidence_words
        assert all(
            usage.sense_id is not None
            for usage in proposal.word_usages
            if usage.role == "anchor"
        )
        assert "segment" in proposal.deferred_words


def test_topic_planning_rejects_words_without_two_reliable_topics() -> None:
    with pytest.raises(TopicPlanningError, match="2-3 curated knowledge topics"):
        planning_service().propose(
            snapshot_id=uuid4(),
            selected_words=["segment", "scope", "draft", "compile"],
            cefr_level="B2",
        )


def test_runtime_planning_supports_arbitrary_unrelated_words() -> None:
    service = planning_service()
    snapshot_id = uuid4()

    result = asyncio.run(
        service.propose_for_runtime(
            snapshot_id=snapshot_id,
            selected_words=["those", "whole"],
            cefr_level="A1",
            exam_goal="CET-4",
            provider=MockLLMProvider(),
        )
    )

    assert result.planning_mode == "language_fallback"
    assert result.unmatched_words == []
    assert {profile.word for profile in result.profiles} == {"those", "whole"}
    assert len(result.proposals) == 2
    for proposal in result.proposals:
        assert len(proposal.anchor_words) == 1
        assert len(proposal.deferred_words) == 1
        assert set(proposal.anchor_words + proposal.deferred_words) == {
            "those",
            "whole",
        }

    proposal = result.proposals[0]
    resolved, brief, profiles = service.resolve_proposal(
        snapshot_id=snapshot_id,
        selected_words=["those", "whole"],
        cefr_level="A1",
        proposal_id=proposal.id,
    )
    confirmed = service.confirm(
        proposal=resolved,
        anchor_words=resolved.anchor_words,
        cefr_level="A1",
    )
    assert confirmed.anchor_words == resolved.anchor_words
    assert brief.topic_id == proposal.topic_id
    assert {profile.word for profile in profiles} == {"those", "whole"}


def test_runtime_does_not_use_fixture_topics_with_real_provider() -> None:
    class ProductionLikeProvider(MockLLMProvider):
        name = "openrouter"
        model = "provider/test-model"

    result = asyncio.run(
        planning_service().propose_for_runtime(
            snapshot_id=uuid4(),
            selected_words=["anchor", "estimate", "ambiguous"],
            cefr_level="B2",
            exam_goal="General English",
            provider=ProductionLikeProvider(),
        )
    )

    assert result.planning_mode == "language_fallback"
    assert all(
        profile.source_name == "openrouter-structured-lexical-analysis"
        for profile in result.profiles
    )


def test_anchor_adjustment_rejects_word_without_topic_relation() -> None:
    service = planning_service()
    result = service.propose(
        snapshot_id=uuid4(),
        selected_words=[
            "anchor",
            "estimate",
            "ambiguous",
            "criteria",
            "validate",
            "segment",
        ],
        cefr_level="B2",
    )

    with pytest.raises(TopicPlanningError, match="sense-to-topic relation"):
        service.confirm(
            proposal=result.proposals[0],
            anchor_words=["anchor", "estimate", "segment"],
            cefr_level="B2",
        )


def test_knowledge_gate_rejects_fact_outside_brief() -> None:
    service = planning_service()
    result = service.propose(
        snapshot_id=uuid4(),
        selected_words=["anchor", "estimate", "ambiguous", "criteria", "validate"],
        cefr_level="B2",
    )
    proposal = service.confirm(
        proposal=result.proposals[0],
        anchor_words=result.proposals[0].anchor_words,
        cefr_level="B2",
    )
    brief = service.build_brief(proposal)
    selection = VocabularySelection(
        source_snapshot_id=result.snapshot_id,
        candidate_words=["anchor", "estimate", "ambiguous", "criteria", "validate"],
        anchor_words=proposal.anchor_words,
        support_words=proposal.support_words,
        deferred_words=proposal.deferred_words,
        excluded_words=proposal.excluded_words,
        context_words=[],
        source_categories={},
    )
    context = LessonGenerationContext(
        cefr_level="B2",
        exam_goal="General English",
        selected_words=selection.candidate_words,
        mastered_words_sample=[],
        tracked_word_count=5,
        topic_proposal=proposal,
        knowledge_brief=brief,
        vocabulary_selection=selection,
    )
    content = asyncio.run(MockLLMProvider().generate_lesson(context))
    broken_content = content.model_copy(
        update={
            "knowledge_claims": [
                *content.knowledge_claims,
                KnowledgeClaim(
                    fact_id="invented-core-fact",
                    source_ids=[brief.sources[0].id],
                ),
            ]
        }
    )

    errors = validate_context_lesson(
        broken_content,
        "B2",
        required_target_words=selection.anchor_words,
        topic_proposal=proposal,
        knowledge_brief=brief,
    )

    assert "Knowledge claim invented-core-fact is outside the KnowledgeBrief" in errors
