import json
from dataclasses import dataclass, replace
from typing import Protocol, TypeVar
from uuid import UUID

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError

from app.core.config import Settings, get_settings
from app.providers.knowledge import FixtureKnowledgeLibrary
from app.providers.lexical import FixtureLexicalSource
from app.providers.mock_lesson import build_mock_lesson
from app.providers.mock_topic import build_mock_dynamic_topic_plan
from app.schemas.lesson import (
    CefrLevel,
    ContextLessonContent,
    Exercise,
)
from app.schemas.topic import DynamicTopicPlan, KnowledgeBrief, TopicProposal
from app.services.knowledge_validation import CEFR_ANCHOR_RANGES
from app.services.lesson_validation import CEFR_WORD_RANGES, contains_word
from app.services.topic_planning import TopicPlanningError, TopicPlanningService
from app.services.vocabulary_context import (
    VocabularySelection,
    assign_vocabulary_roles,
)


@dataclass(frozen=True)
class LessonGenerationContext:
    cefr_level: CefrLevel
    exam_goal: str
    selected_words: list[str]
    mastered_words_sample: list[str]
    tracked_word_count: int
    topic_proposal: TopicProposal | None = None
    knowledge_brief: KnowledgeBrief | None = None
    vocabulary_selection: VocabularySelection | None = None
    previous_validation_errors: tuple[str, ...] = ()

    @property
    def selection(self) -> VocabularySelection:
        if self.vocabulary_selection is not None:
            return self.vocabulary_selection
        return VocabularySelection(
            source_snapshot_id=None,
            candidate_words=self.selected_words,
            anchor_words=self.selected_words,
            support_words=[],
            deferred_words=[],
            excluded_words=[],
            context_words=self.mastered_words_sample,
            source_categories={},
        )


@dataclass(frozen=True)
class FeedbackEvaluation:
    is_correct: bool
    feedback_text: str


class LLMProviderError(RuntimeError):
    pass


class LLMProviderConfigurationError(LLMProviderError):
    pass


class LLMProvider(Protocol):
    name: str

    async def plan_topics(
        self,
        *,
        selected_words: list[str],
        cefr_level: CefrLevel,
        exam_goal: str,
    ) -> DynamicTopicPlan: ...

    async def generate_lesson(
        self,
        context: LessonGenerationContext,
    ) -> ContextLessonContent: ...

    async def evaluate_exercise(
        self,
        exercise: Exercise,
        answer: str,
        target_words: list[str],
    ) -> FeedbackEvaluation: ...

    async def summarize_attempt(
        self,
        correct_count: int,
        total_count: int,
        target_words: list[str],
    ) -> str: ...


class MockLLMProvider:
    name = "mock"

    async def plan_topics(
        self,
        *,
        selected_words: list[str],
        cefr_level: CefrLevel,
        exam_goal: str,
    ) -> DynamicTopicPlan:
        del exam_goal
        return build_mock_dynamic_topic_plan(selected_words, cefr_level)

    async def generate_lesson(
        self,
        context: LessonGenerationContext,
    ) -> ContextLessonContent:
        planned_context = context
        minimum, _ = CEFR_ANCHOR_RANGES[context.cefr_level]
        unique_selected_words = {
            word.strip().casefold() for word in context.selected_words if word.strip()
        }
        if (
            context.topic_proposal is None
            and context.knowledge_brief is None
            and len(unique_selected_words) >= minimum
        ):
            planner = TopicPlanningService(
                FixtureLexicalSource(),
                FixtureKnowledgeLibrary(),
            )
            try:
                proposal = planner.propose(
                    snapshot_id=UUID(int=0),
                    selected_words=context.selected_words,
                    cefr_level=context.cefr_level,
                ).proposals[0]
                brief = planner.build_brief(proposal)
                selection = assign_vocabulary_roles(
                    context.selection,
                    anchor_words=proposal.anchor_words,
                    support_words=proposal.support_words,
                    deferred_words=proposal.deferred_words,
                    excluded_words=proposal.excluded_words,
                )
                planned_context = replace(
                    context,
                    topic_proposal=proposal,
                    knowledge_brief=brief,
                    vocabulary_selection=selection,
                )
            except TopicPlanningError:
                pass
        return build_mock_lesson(planned_context)
    async def evaluate_exercise(
        self,
        exercise: Exercise,
        answer: str,
        target_words: list[str],
    ) -> FeedbackEvaluation:
        normalized_answer = answer.strip().casefold()
        if exercise.grading_mode == "rubric":
            expected_words = (
                [exercise.target_word]
                if exercise.target_word is not None
                else target_words
            )
            uses_target_word = any(
                contains_word(normalized_answer, word) for word in expected_words
            )
            has_complete_sentence = len(normalized_answer.split()) >= 4
            if not uses_target_word:
                feedback_text = (
                    f"请使用指定目标词 {exercise.target_word or '中的至少一个目标词'}，"
                    "并写出至少四个词的完整句子。"
                )
            elif not has_complete_sentence:
                feedback_text = "目标词使用正确，但请写出至少四个词的完整句子。"
            else:
                feedback_text = "表达有效，并在语境中使用了指定目标词。下一步可以换一个语境再造句。"
            return FeedbackEvaluation(
                is_correct=uses_target_word and has_complete_sentence,
                feedback_text=feedback_text,
            )

        is_correct = normalized_answer == exercise.expected_answer.strip().casefold()
        if is_correct:
            feedback_text = (
                "回答正确。"
                + exercise.explanation_zh
                + "下一步可以回看原文语境，再用该词造句。"
            )
        else:
            feedback_text = (
                f"还不准确。正确答案是“{exercise.expected_answer}”。"
                + exercise.explanation_zh
                + "请回到原文对应语境，再试一次。"
            )
        return FeedbackEvaluation(
            is_correct=is_correct,
            feedback_text=feedback_text,
        )

    async def summarize_attempt(
        self,
        correct_count: int,
        total_count: int,
        target_words: list[str],
    ) -> str:
        words = "、".join(target_words)
        return (
            f"你完成了 {total_count} 道练习，其中 {correct_count} 道表现稳定。"
            f"本节已为 {words} 保存新的语境证据。"
            "下一节建议优先复习标记为 Review 的题目。"
        )


class FeedbackPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_correct: bool
    feedback_text: str


class SummaryPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str


ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


def _strict_response_schema(response_model: type[BaseModel]) -> dict[str, object]:
    schema = response_model.model_json_schema(by_alias=True)

    def normalize(node: object) -> None:
        if isinstance(node, dict):
            node.pop("default", None)
            properties = node.get("properties")
            if isinstance(properties, dict):
                node["required"] = list(properties)
            for child in node.values():
                normalize(child)
        elif isinstance(node, list):
            for child in node:
                normalize(child)

    normalize(schema)
    return schema


class OpenRouterLLMProvider:
    name = "openrouter"

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        http_referer: str | None = None,
        app_title: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.http_referer = http_referer
        self.app_title = app_title
        self.client = client

    async def _structured_completion(
        self,
        response_model: type[ResponseModel],
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> ResponseModel:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.http_referer:
            headers["HTTP-Referer"] = self.http_referer
        if self.app_title:
            headers["X-OpenRouter-Title"] = self.app_title

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "strict": True,
                    "schema": _strict_response_schema(response_model),
                },
            },
        }

        try:
            if self.client is not None:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
            else:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
            response.raise_for_status()
            message_content = response.json()["choices"][0]["message"]["content"]
            if not isinstance(message_content, str):
                raise TypeError("OpenRouter message content is not text")
            return response_model.model_validate_json(message_content)
        except httpx.HTTPStatusError as exc:
            detail = ""
            try:
                error_payload = exc.response.json().get("error", {})
                error_message = error_payload.get("message")
                metadata = error_payload.get("metadata", {})
                raw_message = metadata.get("raw") if isinstance(metadata, dict) else None
                messages = [
                    message
                    for message in (error_message, raw_message)
                    if isinstance(message, str) and message
                ]
                if messages:
                    detail = ": " + " | ".join(messages)[:300]
            except (AttributeError, TypeError, ValueError):
                pass
            raise LLMProviderError(
                f"OpenRouter returned HTTP {exc.response.status_code}{detail}"
            ) from exc
        except httpx.RequestError as exc:
            raise LLMProviderError("OpenRouter request failed") from exc
        except (KeyError, IndexError, TypeError, ValueError, ValidationError) as exc:
            raise LLMProviderError("OpenRouter returned invalid structured output") from exc

    async def plan_topics(
        self,
        *,
        selected_words: list[str],
        cefr_level: CefrLevel,
        exam_goal: str,
    ) -> DynamicTopicPlan:
        return await self._structured_completion(
            DynamicTopicPlan,
            system_prompt=(
                "Create 2-3 structured English-learning language TopicProposal candidates. "
                "Return a WordSemanticProfile for every selected word and classify every "
                "selected word exactly once in every candidate. Bind each Anchor word to one "
                "senseId and one RelationEvidence item. Use one or more Anchor words, but never "
                "force unrelated words together: create separate candidates and mark unused "
                "words Deferred. Provide Chinese meanings, part of speech, collocations, "
                "register, semantic domains, and clear relation explanations. Candidate facts "
                "must be limited to word meaning, grammar, collocation, register, or contextual "
                "usage. Do not introduce external factual claims, named studies, statistics, "
                "historical claims, or source URLs. coreFact and supportingFacts must be concise "
                "language facts that can safely bound the later lesson. Use only the content "
                "modes explanatory_scenario, micro_case, and comparison. sourceName and "
                "sourceVersion are provenance placeholders and will be overwritten by Lexis."
            ),
            user_prompt=json.dumps(
                {
                    "selectedWords": selected_words,
                    "cefrLevel": cefr_level,
                    "examGoal": exam_goal,
                },
                ensure_ascii=False,
            ),
        )

    async def generate_lesson(
        self,
        context: LessonGenerationContext,
    ) -> ContextLessonContent:
        minimum, maximum = CEFR_WORD_RANGES[context.cefr_level]
        return await self._structured_completion(
            ContextLessonContent,
            system_prompt=(
                f"Create one CEFR-matched English context lesson for CEFR {context.cefr_level}. "
                f"Hard constraint: readingText must contain between {minimum} and {maximum} "
                "words, inclusive. Count words using whitespace-separated tokens, matching "
                "the backend validator. Count the words before returning the final object and "
                "revise the passage if it is outside this range; never exceed the maximum. "
                "If previousValidationErrors is not empty, treat every listed error as a "
                "required repair before returning the new object. Return only the requested "
                "structured object. Include exactly four exercises with types "
                "vocabulary_context, syntax, paragraph_logic, and output. Keep additional "
                "unfamiliar words at five or fewer. Provide Chinese vocabulary aid, grammar "
                "analysis, expected answers, Chinese explanations, and exercise traceability. "
                "Every unfamiliarWords.word must occur in readingText. For exact_match "
                "exercises, expectedAnswer must be exactly one of options. "
                "Use exactly these semantic values: gradingMode must be exact_match for "
                "vocabulary_context, syntax, and paragraph_logic, and rubric only for output. "
                "Use the supplied TopicProposal and KnowledgeBrief as the factual boundary. "
                "Return topicId, contentMode, coreQuestion, wordUsages, knowledgeTakeaway, "
                "knowledgeSources, and knowledgeClaims. Every knowledgeClaims.factId must be "
                "one of the fact IDs in KnowledgeBrief, and every claim sourceId must be one "
                "of that fact's source IDs. Do not add a new core fact. targetWords must equal "
                "the confirmed Anchor words. Support words are optional; Deferred and Excluded "
                "words must not appear as targetWords. The paragraph_logic exercise checks core "
                "knowledge; the output exercise uses one Anchor word in a new situation. "
                "sourceReference must be exactly target_words or match "
                "reading:sentence-N:marker, where N is a 1-based sentence number in readingText "
                "and every hyphen-separated marker word must occur in that sentence. "
                "vocabulary_context targetWord must be one of anchorWords and its "
                "sourceReference must contain that target word. syntax and paragraph_logic "
                "targetWord must be null. output sourceReference must be target_words and "
                "gradingMode must be rubric. Do not use paragraph-3, section-, or any other "
                "sourceReference format. Every exercise must include skill and a non-empty rubric."
            ),
            user_prompt=json.dumps(
                {
                    "cefrLevel": context.cefr_level,
                    "examGoal": context.exam_goal,
                    "readingWordRange": {"min": minimum, "max": maximum},
                    "previousValidationErrors": list(context.previous_validation_errors),
                    "candidateWords": context.selection.candidate_words,
                    "anchorWords": context.selection.anchor_words,
                    "supportWords": context.selection.support_words,
                    "deferredWords": context.selection.deferred_words,
                    "contextWords": context.selection.context_words,
                    "excludedWords": context.selection.excluded_words,
                    "wordSourceCategories": context.selection.source_categories,
                    "topicProposal": (
                        context.topic_proposal.model_dump(mode="json", by_alias=True)
                        if context.topic_proposal is not None
                        else None
                    ),
                    "knowledgeBrief": (
                        context.knowledge_brief.model_dump(mode="json", by_alias=True)
                        if context.knowledge_brief is not None
                        else None
                    ),
                    "sourceSnapshotId": (
                        str(context.selection.source_snapshot_id)
                        if context.selection.source_snapshot_id is not None
                        else None
                    ),
                    "trackedWordCount": context.tracked_word_count,
                },
                ensure_ascii=False,
            ),
        )

    async def evaluate_exercise(
        self,
        exercise: Exercise,
        answer: str,
        target_words: list[str],
    ) -> FeedbackEvaluation:
        payload = await self._structured_completion(
            FeedbackPayload,
            system_prompt=(
                "Evaluate one English-learning exercise answer. Return a fair boolean result "
                "and concise Chinese feedback. For output practice, accept valid alternatives "
                "that use the specified targetWord naturally. For incorrect answers, state "
                "the correct answer, explain the mistake briefly, and give one concrete next "
                "step."
            ),
            user_prompt=json.dumps(
                {
                    "exercise": exercise.model_dump(mode="json", by_alias=True),
                    "answer": answer,
                    "targetWords": target_words,
                },
                ensure_ascii=False,
            ),
        )
        return FeedbackEvaluation(
            is_correct=payload.is_correct,
            feedback_text=payload.feedback_text,
        )

    async def summarize_attempt(
        self,
        correct_count: int,
        total_count: int,
        target_words: list[str],
    ) -> str:
        payload = await self._structured_completion(
            SummaryPayload,
            system_prompt=(
                "Write a concise Chinese final summary for an English lesson attempt. "
                "Mention performance, saved target-word evidence, and one practical next step."
            ),
            user_prompt=json.dumps(
                {
                    "correctCount": correct_count,
                    "totalCount": total_count,
                    "targetWords": target_words,
                },
                ensure_ascii=False,
            ),
        )
        return payload.summary


class UnavailableLLMProvider:
    name = "unavailable"

    def __init__(self, message: str) -> None:
        self.message = message

    async def plan_topics(
        self,
        *,
        selected_words: list[str],
        cefr_level: CefrLevel,
        exam_goal: str,
    ) -> DynamicTopicPlan:
        del selected_words, cefr_level, exam_goal
        raise LLMProviderConfigurationError(self.message)

    async def generate_lesson(
        self,
        context: LessonGenerationContext,
    ) -> ContextLessonContent:
        raise LLMProviderConfigurationError(self.message)

    async def evaluate_exercise(
        self,
        exercise: Exercise,
        answer: str,
        target_words: list[str],
    ) -> FeedbackEvaluation:
        raise LLMProviderConfigurationError(self.message)

    async def summarize_attempt(
        self,
        correct_count: int,
        total_count: int,
        target_words: list[str],
    ) -> str:
        raise LLMProviderConfigurationError(self.message)


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "mock":
        return MockLLMProvider()

    api_key = settings.openrouter_api_key.get_secret_value() if settings.openrouter_api_key else ""
    if not api_key or not settings.openrouter_model:
        return UnavailableLLMProvider("OpenRouter requires OPENROUTER_API_KEY and OPENROUTER_MODEL")
    return OpenRouterLLMProvider(
        api_key=api_key,
        base_url=settings.openrouter_base_url,
        model=settings.openrouter_model,
        http_referer=settings.openrouter_http_referer,
        app_title=settings.openrouter_app_title,
    )


def get_llm_provider() -> LLMProvider:
    return build_llm_provider(get_settings())
