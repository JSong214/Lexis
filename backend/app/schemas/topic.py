import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.maimemo import to_camel

WordRole = Literal["anchor", "support", "deferred", "excluded"]
ContentMode = Literal["explanatory_scenario", "micro_case", "comparison"]


class TopicApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
        extra="forbid",
    )


class WordSense(TopicApiModel):
    id: str
    definition: str
    meaning_zh: str
    part_of_speech: str
    collocations: list[str] = Field(default_factory=list)
    usage_register: str = Field(default="neutral", alias="register")
    semantic_domains: list[str] = Field(default_factory=list)


class WordSemanticProfile(TopicApiModel):
    word: str
    lemma: str
    difficulty: str
    senses: list[WordSense] = Field(min_length=1)
    source_name: str
    source_version: str


class KnowledgeSource(TopicApiModel):
    id: str
    title: str
    publisher: str
    url: str
    version: str


class KnowledgeFact(TopicApiModel):
    id: str
    text: str
    source_ids: list[str] = Field(min_length=1)


class TopicWordUsage(TopicApiModel):
    word: str
    role: WordRole
    sense_id: str | None = None
    meaning_zh: str | None = None
    part_of_speech: str | None = None
    topic_role: str | None = None
    relation_type: str | None = None


class RelationEvidence(TopicApiModel):
    word: str
    sense_id: str
    topic_role: str
    relation_type: str
    explanation: str


class TopicProposal(TopicApiModel):
    id: str
    topic_id: str
    title: str
    core_question: str
    core_knowledge: str
    content_mode: ContentMode
    word_usages: list[TopicWordUsage]
    relation_evidence: list[RelationEvidence]
    deferred_words: list[str]
    excluded_words: list[str]
    relation_explanation: str
    rationale: str

    @property
    def anchor_words(self) -> list[str]:
        return [item.word for item in self.word_usages if item.role == "anchor"]

    @property
    def support_words(self) -> list[str]:
        return [item.word for item in self.word_usages if item.role == "support"]


class KnowledgeBrief(TopicApiModel):
    topic_id: str
    title: str
    core_question: str
    core_fact: KnowledgeFact
    supporting_facts: list[KnowledgeFact] = Field(default_factory=list, max_length=2)
    causal_explanation: str
    sources: list[KnowledgeSource] = Field(min_length=1)
    content_mode: ContentMode

    @property
    def allowed_fact_ids(self) -> set[str]:
        return {self.core_fact.id, *(fact.id for fact in self.supporting_facts)}


class DynamicTopicCandidate(TopicApiModel):
    title: str
    core_question: str
    core_knowledge: str
    content_mode: ContentMode
    word_usages: list[TopicWordUsage] = Field(min_length=1)
    relation_evidence: list[RelationEvidence] = Field(min_length=1)
    relation_explanation: str
    rationale: str
    core_fact: str
    supporting_facts: list[str] = Field(default_factory=list, max_length=2)
    causal_explanation: str


class DynamicTopicPlan(TopicApiModel):
    profiles: list[WordSemanticProfile] = Field(min_length=1)
    candidates: list[DynamicTopicCandidate] = Field(min_length=2, max_length=3)


class TopicProposalRequest(TopicApiModel):
    cefr_level: Literal["A1", "A2", "B1", "B2", "C1", "C2"] = "B2"
    exam_goal: str = Field(default="General English", max_length=120)
    selected_words: list[str] = Field(min_length=1, max_length=16)


class TopicProposalResponse(TopicApiModel):
    snapshot_id: uuid.UUID
    profiles: list[WordSemanticProfile]
    proposals: list[TopicProposal] = Field(min_length=2, max_length=3)
    unmatched_words: list[str]
    planning_mode: Literal["curated", "language_fallback"] = "curated"
    notice: str | None = None


class KnowledgeClaim(TopicApiModel):
    fact_id: str
    source_ids: list[str] = Field(min_length=1)

