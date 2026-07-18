from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol
from uuid import UUID

from app.providers.knowledge import KnowledgeLibrary, KnowledgeTopic
from app.providers.lexical import LexicalSource
from app.schemas.lesson import CefrLevel
from app.schemas.topic import (
    DynamicTopicPlan,
    KnowledgeBrief,
    KnowledgeFact,
    KnowledgeSource,
    RelationEvidence,
    TopicProposal,
    TopicProposalResponse,
    TopicWordUsage,
    WordSemanticProfile,
)
from app.services.knowledge_validation import CEFR_ANCHOR_RANGES


class TopicPlanningError(ValueError):
    pass


class TopicPlanningProvider(Protocol):
    name: str

    async def plan_topics(
        self,
        *,
        selected_words: list[str],
        cefr_level: CefrLevel,
        exam_goal: str,
    ) -> DynamicTopicPlan: ...


@dataclass(frozen=True)
class StoredTopicPlan:
    proposal: TopicProposal
    brief: KnowledgeBrief
    profiles: tuple[WordSemanticProfile, ...]
    selected_word_keys: frozenset[str]


class TopicPlanningService:
    def __init__(
        self,
        lexical_source: LexicalSource,
        knowledge_library: KnowledgeLibrary,
    ) -> None:
        self.lexical_source = lexical_source
        self.knowledge_library = knowledge_library
        self._runtime_plans: dict[tuple[UUID, str], StoredTopicPlan] = {}

    async def propose_for_runtime(
        self,
        *,
        snapshot_id: UUID,
        selected_words: list[str],
        cefr_level: CefrLevel,
        exam_goal: str,
        provider: TopicPlanningProvider,
    ) -> TopicProposalResponse:
        if provider.name == "mock" or self.knowledge_library.runtime_enabled:
            try:
                return self.propose(
                    snapshot_id=snapshot_id,
                    selected_words=selected_words,
                    cefr_level=cefr_level,
                )
            except TopicPlanningError:
                pass

        dynamic_plan = await provider.plan_topics(
            selected_words=selected_words,
            cefr_level=cefr_level,
            exam_goal=exam_goal,
        )
        return self._register_dynamic_plan(
            snapshot_id=snapshot_id,
            selected_words=selected_words,
            cefr_level=cefr_level,
            provider=provider,
            dynamic_plan=dynamic_plan,
        )

    def propose(
        self,
        *,
        snapshot_id: UUID,
        selected_words: list[str],
        cefr_level: CefrLevel,
    ) -> TopicProposalResponse:
        profiles, unmatched_words = self.lexical_source.enrich(selected_words)
        profile_by_key = {profile.word.casefold(): profile for profile in profiles}
        proposals = [
            proposal
            for topic in self.knowledge_library.list_topics()
            if (
                proposal := self._proposal_for_topic(
                    topic=topic,
                    selected_words=selected_words,
                    profile_by_key=profile_by_key,
                    unmatched_words=unmatched_words,
                    cefr_level=cefr_level,
                )
            )
            is not None
        ]
        proposals.sort(
            key=lambda item: (
                -sum(usage.role in {"anchor", "support"} for usage in item.word_usages),
                item.id,
            )
        )
        proposals = proposals[:3]
        if len(proposals) < 2:
            raise TopicPlanningError(
                "The selected words do not match 2-3 curated knowledge topics."
            )
        return TopicProposalResponse(
            snapshot_id=snapshot_id,
            profiles=profiles,
            proposals=proposals,
            unmatched_words=unmatched_words,
        )

    def resolve_proposal(
        self,
        *,
        snapshot_id: UUID,
        selected_words: list[str],
        cefr_level: CefrLevel,
        proposal_id: str,
    ) -> tuple[TopicProposal, KnowledgeBrief, list[WordSemanticProfile]]:
        stored = self._runtime_plans.get((snapshot_id, proposal_id))
        selected_word_keys = frozenset(
            word.strip().casefold() for word in selected_words if word.strip()
        )
        if stored is not None:
            if selected_word_keys != stored.selected_word_keys:
                raise TopicPlanningError(
                    "The selected words changed after the TopicProposal was created."
                )
            return stored.proposal, stored.brief, list(stored.profiles)

        proposal_result = self.propose(
            snapshot_id=snapshot_id,
            selected_words=selected_words,
            cefr_level=cefr_level,
        )
        proposal = next(
            (item for item in proposal_result.proposals if item.id == proposal_id),
            None,
        )
        if proposal is None:
            raise TopicPlanningError("The selected TopicProposal is stale or unavailable.")
        return proposal, self.build_brief(proposal), proposal_result.profiles

    def confirm(
        self,
        *,
        proposal: TopicProposal,
        anchor_words: list[str],
        cefr_level: CefrLevel,
    ) -> TopicProposal:
        requested = self._unique_words(anchor_words) or proposal.anchor_words
        recommended_minimum, maximum = CEFR_ANCHOR_RANGES[cefr_level]
        if not 1 <= len(requested) <= maximum:
            raise TopicPlanningError(
                f"{cefr_level} allows 1-{maximum} Anchor words; "
                f"{recommended_minimum}-{maximum} is recommended. "
                f"Received {len(requested)}."
            )

        usage_by_key = {item.word.casefold(): item for item in proposal.word_usages}
        evidence_keys = {item.word.casefold() for item in proposal.relation_evidence}
        invalid_words = [
            word
            for word in requested
            if (
                word.casefold() not in usage_by_key
                or usage_by_key[word.casefold()].sense_id is None
                or word.casefold() not in evidence_keys
            )
        ]
        if invalid_words:
            raise TopicPlanningError(
                "These words do not have a validated sense-to-topic relation: "
                + ", ".join(invalid_words)
            )

        anchor_keys = {word.casefold() for word in requested}
        word_usages = [
            item.model_copy(
                update={
                    "role": (
                        "anchor"
                        if item.word.casefold() in anchor_keys
                        else "support"
                        if item.sense_id is not None
                        else item.role
                    )
                }
            )
            for item in proposal.word_usages
        ]
        confirmed = proposal.model_copy(update={"word_usages": word_usages})
        self._validate_relation_evidence(confirmed)
        return confirmed

    def build_brief(self, proposal: TopicProposal) -> KnowledgeBrief:
        topic = self.knowledge_library.get_topic(proposal.topic_id)
        if topic is None:
            raise TopicPlanningError("The selected knowledge topic is no longer available.")
        return KnowledgeBrief(
            topic_id=topic.id,
            title=topic.title,
            core_question=topic.core_question,
            core_fact=topic.core_fact,
            supporting_facts=list(topic.supporting_facts[:2]),
            causal_explanation=topic.causal_explanation,
            sources=list(topic.sources),
            content_mode=topic.content_mode,
        )

    def _register_dynamic_plan(
        self,
        *,
        snapshot_id: UUID,
        selected_words: list[str],
        cefr_level: CefrLevel,
        provider: TopicPlanningProvider,
        dynamic_plan: DynamicTopicPlan,
    ) -> TopicProposalResponse:
        self._validate_dynamic_plan(
            dynamic_plan,
            selected_words=selected_words,
            cefr_level=cefr_level,
        )
        provider_version = self._provider_version(provider)
        profiles = [
            profile.model_copy(
                update={
                    "source_name": f"{provider.name}-structured-lexical-analysis",
                    "source_version": provider_version,
                }
            )
            for profile in dynamic_plan.profiles
        ]
        selected_word_keys = frozenset(
            word.strip().casefold() for word in selected_words if word.strip()
        )
        plan_digest = sha256(
            (
                str(snapshot_id)
                + "|"
                + "|".join(sorted(selected_word_keys))
                + "|"
                + provider.name
                + "|"
                + provider_version
            ).encode("utf-8")
        ).hexdigest()[:12]
        source = KnowledgeSource(
            id=f"language-analysis-{plan_digest}",
            title="AI-generated structured language analysis",
            publisher=f"Lexis via {provider.name}",
            url=(
                "https://openrouter.ai/"
                if provider.name == "openrouter"
                else "https://example.com/lexis/mock-language-analysis"
            ),
            version=provider_version,
        )

        proposals: list[TopicProposal] = []
        for index, candidate in enumerate(dynamic_plan.candidates):
            topic_digest = sha256(
                f"{plan_digest}|{index}|{candidate.title}".encode()
            ).hexdigest()[:12]
            topic_id = f"language-{topic_digest}"
            proposal = TopicProposal(
                id=topic_id,
                topic_id=topic_id,
                title=candidate.title,
                core_question=candidate.core_question,
                core_knowledge=candidate.core_knowledge,
                content_mode=candidate.content_mode,
                word_usages=candidate.word_usages,
                relation_evidence=candidate.relation_evidence,
                deferred_words=[
                    item.word for item in candidate.word_usages if item.role == "deferred"
                ],
                excluded_words=[
                    item.word for item in candidate.word_usages if item.role == "excluded"
                ],
                relation_explanation=candidate.relation_explanation,
                rationale=candidate.rationale,
            )
            core_fact = KnowledgeFact(
                id=f"{topic_id}-core",
                text=candidate.core_fact,
                source_ids=[source.id],
            )
            supporting_facts = [
                KnowledgeFact(
                    id=f"{topic_id}-support-{fact_index + 1}",
                    text=fact_text,
                    source_ids=[source.id],
                )
                for fact_index, fact_text in enumerate(candidate.supporting_facts[:2])
            ]
            brief = KnowledgeBrief(
                topic_id=topic_id,
                title=candidate.title,
                core_question=candidate.core_question,
                core_fact=core_fact,
                supporting_facts=supporting_facts,
                causal_explanation=candidate.causal_explanation,
                sources=[source],
                content_mode=candidate.content_mode,
            )
            proposals.append(proposal)
            self._runtime_plans[(snapshot_id, topic_id)] = StoredTopicPlan(
                proposal=proposal,
                brief=brief,
                profiles=tuple(profiles),
                selected_word_keys=selected_word_keys,
            )

        while len(self._runtime_plans) > 256:
            self._runtime_plans.pop(next(iter(self._runtime_plans)))

        return TopicProposalResponse(
            snapshot_id=snapshot_id,
            profiles=profiles,
            proposals=proposals,
            unmatched_words=[],
            planning_mode="language_fallback",
            notice=(
                "No curated factual topic matched. These proposals teach word meaning, "
                "grammar, or usage and do not introduce unsupported external facts."
            ),
        )

    @staticmethod
    def _validate_dynamic_plan(
        dynamic_plan: DynamicTopicPlan,
        *,
        selected_words: list[str],
        cefr_level: CefrLevel,
    ) -> None:
        selected_by_key = {
            word.strip().casefold(): word.strip()
            for word in selected_words
            if word.strip()
        }
        profile_by_key = {
            profile.word.casefold(): profile for profile in dynamic_plan.profiles
        }
        if set(profile_by_key) != set(selected_by_key):
            raise TopicPlanningError(
                "Dynamic lexical profiles must exactly match the selected words."
            )

        _, maximum = CEFR_ANCHOR_RANGES[cefr_level]
        for candidate in dynamic_plan.candidates:
            usage_by_key = {
                usage.word.casefold(): usage for usage in candidate.word_usages
            }
            if (
                set(usage_by_key) != set(selected_by_key)
                or len(usage_by_key) != len(candidate.word_usages)
            ):
                raise TopicPlanningError(
                    "Every TopicProposal must classify each selected word exactly once."
                )
            anchors = [
                usage for usage in candidate.word_usages if usage.role == "anchor"
            ]
            if not 1 <= len(anchors) <= maximum:
                raise TopicPlanningError(
                    f"Dynamic TopicProposal must use 1-{maximum} Anchor words."
                )

            evidence = {
                (item.word.casefold(), item.sense_id)
                for item in candidate.relation_evidence
            }
            for anchor in anchors:
                profile = profile_by_key[anchor.word.casefold()]
                profile_sense_ids = {sense.id for sense in profile.senses}
                if (
                    anchor.sense_id is None
                    or anchor.sense_id not in profile_sense_ids
                    or (anchor.word.casefold(), anchor.sense_id) not in evidence
                ):
                    raise TopicPlanningError(
                        f"Anchor word {anchor.word} lacks a validated lexical sense relation."
                    )
            if not candidate.core_fact.strip() or not candidate.causal_explanation.strip():
                raise TopicPlanningError(
                    "Dynamic language topics require one core fact and an explanation."
                )

    def _proposal_for_topic(
        self,
        *,
        topic: KnowledgeTopic,
        selected_words: list[str],
        profile_by_key: dict[str, WordSemanticProfile],
        unmatched_words: list[str],
        cefr_level: CefrLevel,
    ) -> TopicProposal | None:
        minimum, maximum = CEFR_ANCHOR_RANGES[cefr_level]
        selected_by_key = {
            word.strip().casefold(): word.strip()
            for word in selected_words
            if word.strip()
        }
        matched_keys = [
            key
            for key in topic.anchor_priority
            if key in selected_by_key
            and key in profile_by_key
            and self._find_matching_sense(profile_by_key[key], topic, key) is not None
        ]
        if not matched_keys:
            return None

        default_count = min(max(3, minimum), maximum, len(matched_keys))
        anchor_keys = set(matched_keys[:default_count])
        matched_key_set = set(matched_keys)
        unmatched_keys = {word.casefold() for word in unmatched_words}
        usages: list[TopicWordUsage] = []
        evidence: list[RelationEvidence] = []
        for key, original_word in selected_by_key.items():
            profile = profile_by_key.get(key)
            rule = topic.word_rules.get(key)
            sense = (
                self._find_matching_sense(profile, topic, key)
                if profile is not None and rule is not None
                else None
            )
            if key in anchor_keys:
                role = "anchor"
            elif key in matched_key_set:
                role = "support"
            elif key in unmatched_keys:
                role = "excluded"
            else:
                role = "deferred"
            usages.append(
                TopicWordUsage(
                    word=original_word,
                    role=role,
                    sense_id=sense.id if sense is not None else None,
                    meaning_zh=sense.meaning_zh if sense is not None else None,
                    part_of_speech=sense.part_of_speech if sense is not None else None,
                    topic_role=rule.topic_role if sense is not None and rule is not None else None,
                    relation_type=(
                        rule.relation_type if sense is not None and rule is not None else None
                    ),
                )
            )
            if sense is not None and rule is not None:
                evidence.append(
                    RelationEvidence(
                        word=original_word,
                        sense_id=sense.id,
                        topic_role=rule.topic_role,
                        relation_type=rule.relation_type,
                        explanation=rule.explanation,
                    )
                )

        proposal = TopicProposal(
            id=topic.id,
            topic_id=topic.id,
            title=topic.title,
            core_question=topic.core_question,
            core_knowledge=topic.core_knowledge,
            content_mode=topic.content_mode,
            word_usages=usages,
            relation_evidence=evidence,
            deferred_words=[item.word for item in usages if item.role == "deferred"],
            excluded_words=[item.word for item in usages if item.role == "excluded"],
            relation_explanation=topic.relation_explanation,
            rationale=(
                "Every Anchor word is bound to one lexical sense and a named role inside the "
                "same knowledge frame."
            ),
        )
        self._validate_relation_evidence(proposal)
        return proposal

    @staticmethod
    def _find_matching_sense(
        profile: WordSemanticProfile,
        topic: KnowledgeTopic,
        word_key: str,
    ):
        rule = topic.word_rules.get(word_key)
        if rule is None:
            return None
        return next((sense for sense in profile.senses if sense.id == rule.sense_id), None)

    @staticmethod
    def _validate_relation_evidence(proposal: TopicProposal) -> None:
        evidence = {
            (item.word.casefold(), item.sense_id) for item in proposal.relation_evidence
        }
        missing = [
            item.word
            for item in proposal.word_usages
            if item.role == "anchor"
            and (
                item.sense_id is None
                or (item.word.casefold(), item.sense_id) not in evidence
            )
        ]
        if missing:
            raise TopicPlanningError(
                "Anchor words are missing relation evidence: " + ", ".join(missing)
            )

    @staticmethod
    def _provider_version(provider: TopicPlanningProvider) -> str:
        for attribute in ("model", "model_name"):
            value = getattr(provider, attribute, None)
            if isinstance(value, str) and value:
                return value
        return provider.name

    @staticmethod
    def _unique_words(words: list[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for word in words:
            normalized = word.strip().casefold()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            result.append(word.strip())
        return result
