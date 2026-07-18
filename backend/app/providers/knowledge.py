from dataclasses import dataclass, replace
from typing import Protocol

from app.schemas.topic import ContentMode, KnowledgeFact, KnowledgeSource


@dataclass(frozen=True)
class TopicWordRule:
    sense_id: str
    topic_role: str
    relation_type: str
    explanation: str


@dataclass(frozen=True)
class KnowledgeTopic:
    id: str
    title: str
    core_question: str
    core_knowledge: str
    content_mode: ContentMode
    core_fact: KnowledgeFact
    supporting_facts: tuple[KnowledgeFact, ...]
    causal_explanation: str
    sources: tuple[KnowledgeSource, ...]
    anchor_priority: tuple[str, ...]
    word_rules: dict[str, TopicWordRule]
    relation_explanation: str


class KnowledgeLibrary(Protocol):
    name: str
    version: str
    runtime_enabled: bool

    def list_topics(self) -> list[KnowledgeTopic]: ...

    def get_topic(self, topic_id: str) -> KnowledgeTopic | None: ...


ANCHORING_SOURCE = KnowledgeSource(
    id="tversky-kahneman-1974",
    title="Judgment under Uncertainty: Heuristics and Biases",
    publisher="Science",
    url="https://doi.org/10.1126/science.185.4157.1124",
    version="1974",
)
UNCERTAINTY_SOURCE = KnowledgeSource(
    id="nist-tn-1297",
    title="Guidelines for Evaluating and Expressing the Uncertainty of NIST Measurement Results",
    publisher="National Institute of Standards and Technology",
    url="https://www.nist.gov/pml/nist-technical-note-1297",
    version="1994 edition",
)
REPRODUCIBILITY_SOURCE = KnowledgeSource(
    id="nas-reproducibility-2019",
    title="Reproducibility and Replicability in Science",
    publisher="National Academies of Sciences, Engineering, and Medicine",
    url="https://doi.org/10.17226/25303",
    version="2019",
)
RETRIEVAL_SOURCE = KnowledgeSource(
    id="karpicke-blunt-2011",
    title="Retrieval Practice Produces More Learning than Elaborative Studying",
    publisher="Science",
    url="https://doi.org/10.1126/science.1199327",
    version="2011",
)


FIXTURE_TOPICS = (
    KnowledgeTopic(
        id="anchoring-changes-estimates",
        title="Why the first number can change your estimate",
        core_question="Why can an initial number pull later estimates toward it?",
        core_knowledge=(
            "An initial value can become an anchor that influences later numerical judgments, "
            "even when the starting value is weak evidence."
        ),
        content_mode="micro_case",
        core_fact=KnowledgeFact(
            id="anchoring-core",
            text=(
                "An initial numerical value can act as an anchor and pull later estimates "
                "toward it."
            ),
            source_ids=[ANCHORING_SOURCE.id],
        ),
        supporting_facts=(
            KnowledgeFact(
                id="anchoring-support-arbitrary",
                text="Starting values can influence estimates even when they are arbitrary.",
                source_ids=[ANCHORING_SOURCE.id],
            ),
        ),
        causal_explanation=(
            "The first value supplies a reference point; later judgment adjusts away from it, "
            "but the adjustment may be incomplete."
        ),
        sources=(ANCHORING_SOURCE,),
        anchor_priority=("anchor", "estimate", "ambiguous", "criteria", "validate"),
        word_rules={
            "anchor": TopicWordRule(
                "anchor.reference_point",
                "the initial reference value",
                "starting-point",
                "anchor names the reference point that influences the later judgment.",
            ),
            "estimate": TopicWordRule(
                "estimate.approximate_judgment",
                "the judgment being influenced",
                "affected-result",
                "estimate names the approximate judgment that moves toward the anchor.",
            ),
            "ambiguous": TopicWordRule(
                "ambiguous.open_to_interpretation",
                "uncertain input",
                "uncertainty-condition",
                "ambiguous information leaves room for the starting value to guide judgment.",
            ),
            "criteria": TopicWordRule(
                "criteria.judging_standards",
                "explicit standards used to check the estimate",
                "bias-reduction",
                "criteria provide an alternative basis for judging the estimate.",
            ),
            "validate": TopicWordRule(
                "validate.check_soundness",
                "the act of checking the estimate against evidence",
                "evidence-check",
                "validate describes checking whether the estimate survives evidence.",
            ),
        },
        relation_explanation=(
            "The words describe one judgment process: ambiguous evidence invites an anchor, "
            "the anchor influences an estimate, and criteria can be used to validate it."
        ),
    ),
    KnowledgeTopic(
        id="uncertainty-needs-a-range",
        title="Why one number can hide uncertainty",
        core_question="Why is a range sometimes more informative than one estimate?",
        core_knowledge=(
            "A measurement result is more informative when it communicates uncertainty, "
            "because one point value can hide the range of values reasonably supported."
        ),
        content_mode="comparison",
        core_fact=KnowledgeFact(
            id="uncertainty-core",
            text=(
                "A measurement result is incomplete when it gives no quantitative statement "
                "of its uncertainty."
            ),
            source_ids=[UNCERTAINTY_SOURCE.id],
        ),
        supporting_facts=(
            KnowledgeFact(
                id="uncertainty-support-dispersion",
                text=(
                    "Measurement uncertainty characterizes the dispersion of values that could "
                    "reasonably be attributed to the measured quantity."
                ),
                source_ids=[UNCERTAINTY_SOURCE.id],
            ),
        ),
        causal_explanation=(
            "A single point suppresses information about dispersion; a range makes that "
            "uncertainty visible and gives readers clearer criteria for interpretation."
        ),
        sources=(UNCERTAINTY_SOURCE,),
        anchor_priority=("estimate", "ambiguous", "criteria", "validate", "anchor"),
        word_rules={
            "estimate": TopicWordRule(
                "estimate.approximate_judgment",
                "the reported point value",
                "reported-result",
                "estimate names the approximate value being communicated.",
            ),
            "ambiguous": TopicWordRule(
                "ambiguous.open_to_interpretation",
                "the risk created by hidden uncertainty",
                "interpretation-risk",
                "ambiguous describes how one number can support more than one interpretation.",
            ),
            "criteria": TopicWordRule(
                "criteria.judging_standards",
                "standards for interpreting the range",
                "interpretation-rule",
                "criteria specify how the estimate and uncertainty should be interpreted.",
            ),
            "validate": TopicWordRule(
                "validate.check_soundness",
                "checking the reported method",
                "method-check",
                "validate describes checking whether the uncertainty method is sound.",
            ),
            "anchor": TopicWordRule(
                "anchor.reference_point",
                "the point value used as a reference",
                "reference-value",
                "anchor describes the central value around which a range is discussed.",
            ),
        },
        relation_explanation=(
            "The words describe how an estimate is communicated: a point can become an anchor, "
            "uncertainty may remain ambiguous, and criteria help readers validate the range."
        ),
    ),
    KnowledgeTopic(
        id="checkable-methods-build-trust",
        title="Why visible methods make a claim easier to trust",
        core_question="Why does showing a method make a result easier to check?",
        core_knowledge=(
            "A result is easier to evaluate when the method, assumptions, and evidence are "
            "explicit enough for another person to check."
        ),
        content_mode="explanatory_scenario",
        core_fact=KnowledgeFact(
            id="reproducibility-core",
            text=(
                "Reproducibility and replicability help researchers evaluate the reliability "
                "of scientific results."
            ),
            source_ids=[REPRODUCIBILITY_SOURCE.id],
        ),
        supporting_facts=(
            KnowledgeFact(
                id="reproducibility-support-transparency",
                text=(
                    "Transparent reporting of methods and evidence makes a result easier for "
                    "other people to assess."
                ),
                source_ids=[REPRODUCIBILITY_SOURCE.id],
            ),
        ),
        causal_explanation=(
            "Explicit criteria and visible evidence expose the reasoning behind an estimate, "
            "so another person can test the same steps instead of trusting the conclusion alone."
        ),
        sources=(REPRODUCIBILITY_SOURCE,),
        anchor_priority=("criteria", "validate", "estimate", "ambiguous", "anchor"),
        word_rules={
            "criteria": TopicWordRule(
                "criteria.judging_standards",
                "the standards used to judge the result",
                "evaluation-standard",
                "criteria state what a successful check should satisfy.",
            ),
            "validate": TopicWordRule(
                "validate.check_soundness",
                "the act of checking the method and result",
                "verification-action",
                "validate names the action of testing whether the reasoning is sound.",
            ),
            "estimate": TopicWordRule(
                "estimate.approximate_judgment",
                "the result being checked",
                "checked-result",
                "estimate names the approximate result whose basis must be visible.",
            ),
            "ambiguous": TopicWordRule(
                "ambiguous.open_to_interpretation",
                "a description of unclear methods",
                "clarity-risk",
                "ambiguous methods prevent another person from repeating the same check.",
            ),
            "anchor": TopicWordRule(
                "anchor.reference_point",
                "the baseline used for comparison",
                "comparison-baseline",
                "anchor provides a stable baseline against which a result can be compared.",
            ),
        },
        relation_explanation=(
            "The words form an evidence-checking frame: criteria define the test, validate names "
            "the check, and the estimate is compared with an explicit anchor instead of an "
            "ambiguous method."
        ),
    ),
    KnowledgeTopic(
        id="retrieval-strengthens-memory",
        title="Why recalling a word can beat rereading it",
        core_question="Why can trying to recall information strengthen later memory?",
        core_knowledge=(
            "Retrieval practice strengthens later learning because actively recalling information "
            "is itself a learning event, not only a test."
        ),
        content_mode="micro_case",
        core_fact=KnowledgeFact(
            id="retrieval-core",
            text="Retrieval practice can produce more learning than additional studying.",
            source_ids=[RETRIEVAL_SOURCE.id],
        ),
        supporting_facts=(
            KnowledgeFact(
                id="retrieval-support-transfer",
                text="Retrieval practice can support later use of knowledge in new situations.",
                source_ids=[RETRIEVAL_SOURCE.id],
            ),
        ),
        causal_explanation=(
            "Trying to retrieve an answer exercises access to the memory; later review and "
            "application then reinforce that access path."
        ),
        sources=(RETRIEVAL_SOURCE,),
        anchor_priority=("review", "retain", "apply", "reinforce"),
        word_rules={
            "review": TopicWordRule(
                "review.study_again",
                "the later check of recalled material",
                "study-step",
                "review describes returning to material after a retrieval attempt.",
            ),
            "retain": TopicWordRule(
                "retain.keep_in_memory",
                "the desired memory result",
                "learning-result",
                "retain names the goal of keeping information available in memory.",
            ),
            "apply": TopicWordRule(
                "apply.use_in_situation",
                "using recalled knowledge in a new case",
                "transfer-action",
                "apply describes moving recalled knowledge into a new situation.",
            ),
            "reinforce": TopicWordRule(
                "reinforce.make_stronger",
                "strengthening access through practice",
                "strengthening-effect",
                "reinforce describes the effect of repeated successful retrieval.",
            ),
        },
        relation_explanation=(
            "The words describe one memory process: review prompts recall, recall helps retain "
            "knowledge, application transfers it, and repeated retrieval can reinforce access."
        ),
    ),
)
_RETRIEVAL_BASE = FIXTURE_TOPICS[-1]
FIXTURE_TOPICS = (
    *FIXTURE_TOPICS,
    replace(
        _RETRIEVAL_BASE,
        id="retrieval-beats-rereading",
        title="Why recalling can beat another reread",
        core_question="Why can active recall produce more learning than another reread?",
        content_mode="comparison",
        core_knowledge=(
            "Actively retrieving information can produce more learning than spending the "
            "same time on additional study."
        ),
        core_fact=KnowledgeFact(
            id="retrieval-comparison-core",
            text="Retrieval practice can produce more learning than additional studying.",
            source_ids=[RETRIEVAL_SOURCE.id],
        ),
        supporting_facts=(_RETRIEVAL_BASE.core_fact,),
        causal_explanation=(
            "Rereading presents the answer again, while retrieval requires the learner to "
            "reconstruct access to it before receiving feedback."
        ),
    ),
    replace(
        _RETRIEVAL_BASE,
        id="retrieval-supports-transfer",
        title="Why using recalled knowledge tests real learning",
        core_question="Why should recalled knowledge be applied in a new situation?",
        content_mode="explanatory_scenario",
        core_knowledge=(
            "Applying recalled knowledge in a changed situation checks whether the learner "
            "can transfer the idea rather than repeat one memorized example."
        ),
        core_fact=KnowledgeFact(
            id="retrieval-transfer-core",
            text="Retrieval practice can support later use of knowledge in new situations.",
            source_ids=[RETRIEVAL_SOURCE.id],
        ),
        supporting_facts=(_RETRIEVAL_BASE.core_fact,),
        causal_explanation=(
            "A new situation removes cues from the original example, so successful use shows "
            "that the learner can retrieve and apply the underlying meaning."
        ),
    ),
)


class FixtureKnowledgeLibrary:
    name = "lexis-evergreen-fixture"
    version = "2026-07-17-v1"
    runtime_enabled = False

    def list_topics(self) -> list[KnowledgeTopic]:
        return list(FIXTURE_TOPICS)

    def get_topic(self, topic_id: str) -> KnowledgeTopic | None:
        return next((topic for topic in FIXTURE_TOPICS if topic.id == topic_id), None)


def get_knowledge_library() -> KnowledgeLibrary:
    return FixtureKnowledgeLibrary()
