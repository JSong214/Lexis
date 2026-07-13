import json
from dataclasses import dataclass
from typing import Protocol, TypeVar

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError

from app.core.config import Settings, get_settings
from app.schemas.lesson import (
    CefrLevel,
    ContextLessonContent,
    Exercise,
    WordAid,
)
from app.services.lesson_validation import CEFR_WORD_RANGES


@dataclass(frozen=True)
class LessonGenerationContext:
    cefr_level: CefrLevel
    exam_goal: str
    selected_words: list[str]
    mastered_words_sample: list[str]
    tracked_word_count: int


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

    async def generate_lesson(
        self,
        context: LessonGenerationContext,
    ) -> ContextLessonContent:
        minimum, _ = CEFR_WORD_RANGES[context.cefr_level]
        sentences = [
            "A learning team uses a stable anchor when it estimates an uncertain result.",
            "The anchor is not a final answer, but it gives everyone a clear place to begin.",
            "Each person compares the new situation with a familiar segment "
            "and explains the criteria.",
            "The group then adjusts its draft estimate when useful evidence appears.",
            "This method makes hidden reasoning visible and easier to validate.",
            "It also helps the team retain a useful structure without ignoring new context.",
            "When an estimate stays ambiguous, the team asks which assumption "
            "caused the difference.",
            "Careful discussion turns a rough number into a decision that people can understand.",
        ]
        reading_parts: list[str] = []
        index = 0
        while len(" ".join(reading_parts).split()) < minimum:
            reading_parts.append(sentences[index % len(sentences)])
            index += 1
        reading_text = " ".join(reading_parts)
        focus_words = context.selected_words[:8]
        return ContextLessonContent(
            title="Estimating with stable anchors",
            reading_text=reading_text,
            unfamiliar_words=[
                WordAid(word="assumption", meaning_zh="假设"),
                WordAid(word="evidence", meaning_zh="证据"),
            ],
            target_words=focus_words,
            grammar_analysis=[
                "not A, but B：用于修正前半句，并强调后半句。",
                "when + clause：说明动作发生的条件或时间。",
            ],
            exercises=[
                Exercise(
                    type="vocabulary_context",
                    question="What does anchor mean in this reading?",
                    options=["A reference point", "A final answer", "A secret rule"],
                    expected_answer="A reference point",
                    explanation_zh="文中的 anchor 指用于比较的稳定参照点。",
                ),
                Exercise(
                    type="syntax",
                    question="What does the not A, but B structure emphasize?",
                    options=["The second idea", "The first idea", "Neither idea"],
                    expected_answer="The second idea",
                    explanation_zh="该结构否定或弱化 A，并强调 B。",
                ),
                Exercise(
                    type="paragraph_logic",
                    question="Why does the team explain its criteria?",
                    options=[
                        "To make reasoning visible",
                        "To hide uncertainty",
                        "To add more words",
                    ],
                    expected_answer="To make reasoning visible",
                    explanation_zh="文章强调把估算依据公开，便于检查和调整。",
                ),
                Exercise(
                    type="output",
                    question="Write one sentence using a target word.",
                    options=[],
                    expected_answer="A relevant sentence using one target word.",
                    explanation_zh="答案应在清晰语境中正确使用目标词。",
                ),
            ],
        )

    async def evaluate_exercise(
        self,
        exercise: Exercise,
        answer: str,
        target_words: list[str],
    ) -> FeedbackEvaluation:
        normalized_answer = answer.strip().casefold()
        if exercise.type == "output":
            uses_target_word = any(word.casefold() in normalized_answer for word in target_words)
            return FeedbackEvaluation(
                is_correct=uses_target_word,
                feedback_text=(
                    "表达有效，并在语境中使用了目标词。"
                    if uses_target_word
                    else "请至少使用一个目标词，并写出完整、清晰的句子。"
                ),
            )

        is_correct = normalized_answer == exercise.expected_answer.strip().casefold()
        prefix = "回答正确。" if is_correct else "还不准确。"
        return FeedbackEvaluation(
            is_correct=is_correct,
            feedback_text=prefix + exercise.explanation_zh,
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
                    "schema": response_model.model_json_schema(by_alias=True),
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

    async def generate_lesson(
        self,
        context: LessonGenerationContext,
    ) -> ContextLessonContent:
        minimum, maximum = CEFR_WORD_RANGES[context.cefr_level]
        return await self._structured_completion(
            ContextLessonContent,
            system_prompt=(
                "Create one CEFR-matched English context lesson. Return only the requested "
                "structured object. Include exactly four exercises with types "
                "vocabulary_context, syntax, paragraph_logic, and output. Keep additional "
                "unfamiliar words at five or fewer. Provide Chinese vocabulary aid, grammar "
                "analysis, expected answers, and Chinese explanations."
            ),
            user_prompt=json.dumps(
                {
                    "cefrLevel": context.cefr_level,
                    "examGoal": context.exam_goal,
                    "readingWordRange": [minimum, maximum],
                    "selectedWords": context.selected_words,
                    "masteredWordsForContextOnly": context.mastered_words_sample,
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
                "that use a target word naturally."
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
