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
from app.services.lesson_validation import CEFR_WORD_RANGES, contains_word
from app.services.vocabulary_context import VocabularySelection


@dataclass(frozen=True)
class LessonGenerationContext:
    cefr_level: CefrLevel
    exam_goal: str
    selected_words: list[str]
    mastered_words_sample: list[str]
    tracked_word_count: int
    vocabulary_selection: VocabularySelection | None = None

    @property
    def selection(self) -> VocabularySelection:
        if self.vocabulary_selection is not None:
            return self.vocabulary_selection
        return VocabularySelection(
            source_snapshot_id=None,
            required_target_words=self.selected_words,
            priority_words=[],
            context_words=self.mastered_words_sample,
            excluded_words=[],
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
        focus_words = context.selection.required_target_words[:8]
        focus_word_keys = {word.casefold() for word in focus_words}
        practice_focus = bool(focus_word_keys & {"review", "reinforce", "apply"})

        if practice_focus:
            sentences = [
                "Before a new lesson, Maya opens her notes and begins a short review of the words "
                "from last week.",
                "She checks one example, then tries to apply the same rule to a new sentence.",
                "When she makes a mistake, she reads the explanation and tries again "
                "instead of guessing.",
                "Each correct attempt helps reinforce the habit, so the words become "
                "easier to remember.",
                "Her teacher asks her to explain the answer in simple English and compare "
                "it with the model.",
                "At the end, Maya writes one clear sentence and marks the word for another "
                "review tomorrow.",
            ]
            title = "Making Progress Through Review"
            unfamiliar_words = [
                WordAid(word="explanation", meaning_zh="解释"),
                WordAid(word="model", meaning_zh="范例"),
            ]
            grammar_analysis = [
                "when + clause：说明犯错后采取行动的时间或条件。",
                "instead of + -ing：表示没有做某事，而是选择了另一种做法。",
            ]
            syntax_exercise = Exercise(
                type="syntax",
                question="Why does Maya try again instead of guessing?",
                options=[
                    "To reinforce the habit through practice",
                    "To avoid reading the explanation",
                    "To change the lesson topic",
                ],
                expected_answer="To reinforce the habit through practice",
                explanation_zh="文章说明她通过再次练习来巩固记忆，而不是直接猜答案。",
                source_reference="reading:sentence-3:tries-again",
                target_word=None,
                skill="reasoning",
                grading_mode="exact_match",
                rubric=["Connects trying again with reinforcing the learning habit."],
            )
            logic_exercise = Exercise(
                type="paragraph_logic",
                question="Why does Maya mark the word for another review?",
                options=[
                    "To remember it better over time",
                    "To remove it from her notes",
                    "To avoid using it in a sentence",
                ],
                expected_answer="To remember it better over time",
                explanation_zh="再次复习让新词有更多接触机会，帮助形成稳定记忆。",
                source_reference="reading:sentence-6:review",
                target_word=None,
                skill="study_strategy",
                grading_mode="exact_match",
                rubric=["Explains how another review supports memory."],
            )
        else:
            sentences = [
                "A project team uses a stable anchor when it makes an estimate "
                "about a result and starts a review of the evidence behind each assumption.",
                "The anchor is not a final answer, but it gives the team a clear place to begin "
                "and apply a useful pattern.",
                "Each person compares the new segment with a familiar one, defines the criteria, "
                "and explains them so the reasoning is visible to everyone.",
                "The group then adjusts its draft estimate, validates the evidence, "
                "and compiles the notes.",
                "This method makes hidden reasoning visible and easier to validate, "
                "so people can retain a useful structure.",
                "It also helps the team reinforce a stable habit without ignoring new context.",
                "When an estimate stays ambiguous, the team asks which assumption "
                "caused the difference.",
                "Careful discussion turns a rough number into a decision that people can explain "
                "and compare with new evidence.",
            ]
            title = "Adjusting an Estimate with Evidence"
            unfamiliar_words = [
                WordAid(word="assumption", meaning_zh="假设"),
                WordAid(word="evidence", meaning_zh="证据"),
            ]
            grammar_analysis = [
                "not A, but B：用于修正前半句，并强调后半句。",
                "when + clause：说明动作发生的条件或时间。",
            ]
            syntax_exercise = Exercise(
                type="syntax",
                question="What does the not A, but B structure emphasize?",
                options=["The second idea", "The first idea", "Neither idea"],
                expected_answer="The second idea",
                explanation_zh="该结构否定或弱化 A，并强调 B。",
                source_reference="reading:sentence-2:not-A-but",
                target_word=None,
                skill="syntax",
                grading_mode="exact_match",
                rubric=["Identifies which idea the structure emphasizes."],
            )
            logic_exercise = Exercise(
                type="paragraph_logic",
                question="Why does the team explain its criteria?",
                options=[
                    "To make reasoning visible",
                    "To hide uncertainty",
                    "To add more words",
                ],
                expected_answer="To make reasoning visible",
                explanation_zh="文章说明公开 criteria 可以让团队检查和调整 reasoning。",
                source_reference="reading:sentence-3:criteria",
                target_word=None,
                skill="paragraph_logic",
                grading_mode="exact_match",
                rubric=["Connects the criteria with visible reasoning."],
            )

        reading_parts: list[str] = []
        index = 0
        while len(" ".join(reading_parts).split()) < minimum:
            reading_parts.append(sentences[index % len(sentences)])
            index += 1
        while any(
            not contains_word(" ".join(reading_parts), word) for word in focus_words
        ):
            reading_parts.append(sentences[index % len(sentences)])
            index += 1
        reading_text = " ".join(reading_parts)

        def source_for(word: str) -> str:
            for sentence_index, sentence in enumerate(sentences, start=1):
                if contains_word(sentence, word):
                    return f"reading:sentence-{sentence_index}:{word}"
            return "target_words"

        vocabulary_target = focus_words[0] if focus_words else "anchor"
        vocabulary_meanings = {
            "anchor": "A reference point",
            "segment": "A part of something",
            "estimate": "A reasoned rough judgment",
            "criteria": "Standards used for judging",
            "draft": "An early version",
            "validate": "Check that something is sound",
            "retain": "Keep or remember",
            "compile": "Collect into one place",
            "ambiguous": "Open to more than one meaning",
            "scope": "The range covered",
            "review": "A short return to previous material",
            "reinforce": "Make a habit stronger",
            "apply": "Use in a situation",
        }
        vocabulary_answer = vocabulary_meanings.get(
            vocabulary_target.casefold(),
            "A useful reference in the reading",
        )
        output_target = focus_words[0] if focus_words else None
        output_examples = {
            "anchor": "I use an anchor when I estimate the project timeline.",
            "review": "I review the new words before tomorrow's lesson.",
            "reinforce": "Short practice helps reinforce a useful habit.",
            "apply": "I apply the rule to a new sentence.",
        }
        output_answer = output_examples.get(
            output_target.casefold() if output_target else "",
            "I use the target word in a clear sentence.",
        )
        vocabulary_exercise = Exercise(
            type="vocabulary_context",
            source_reference=source_for(vocabulary_target),
            target_word=vocabulary_target,
            question=f"What does {vocabulary_target} mean in this reading?",
            options=[vocabulary_answer, "A final answer", "A secret rule"],
            expected_answer=vocabulary_answer,
            explanation_zh=f"请根据文章语境理解目标词 {vocabulary_target}。",
            skill="vocabulary_in_context",
            grading_mode="exact_match",
            rubric=[f"Defines {vocabulary_target} using the reading context."],
        )
        output_exercise = Exercise(
            type="output",
            question=f"Write one sentence using {output_target or 'a target word'}.",
            options=[],
            expected_answer=output_answer,
            explanation_zh="答案应使用指定目标词，并构成完整、清晰的句子。",
            source_reference="target_words",
            target_word=output_target,
            skill="guided_output",
            grading_mode="rubric",
            rubric=[
                "Uses the specified target word accurately.",
                "Writes a complete sentence of at least four words.",
            ],
        )
        return ContextLessonContent(
            title=title,
            reading_text=reading_text,
            unfamiliar_words=unfamiliar_words,
            target_words=focus_words,
            grammar_analysis=grammar_analysis,
            exercises=[
                vocabulary_exercise,
                syntax_exercise,
                logic_exercise,
                output_exercise,
            ],
        )

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
                "analysis, expected answers, Chinese explanations, and exercise traceability. "
                "Every unfamiliarWords.word must occur in readingText. For exact_match "
                "exercises, expectedAnswer must be exactly one of options. "
                "Use exactly these semantic values: gradingMode must be exact_match for "
                "vocabulary_context, syntax, and paragraph_logic, and rubric only for output. "
                "sourceReference must be exactly target_words or match "
                "reading:sentence-N:marker, where N is a 1-based sentence number in readingText "
                "and every hyphen-separated marker word must occur in that sentence. "
                "vocabulary_context targetWord must be one of requiredTargetWords and its "
                "sourceReference must contain that target word. syntax and paragraph_logic "
                "targetWord must be null. output sourceReference must be target_words and "
                "gradingMode must be rubric. Do not use paragraph-3, section-, or any other "
                "sourceReference format. Every exercise must include skill and a non-empty rubric."
            ),
            user_prompt=json.dumps(
                {
                    "cefrLevel": context.cefr_level,
                    "examGoal": context.exam_goal,
                    "readingWordRange": [minimum, maximum],
                    "requiredTargetWords": context.selection.required_target_words,
                    "priorityWords": context.selection.priority_words,
                    "contextWords": context.selection.context_words,
                    "excludedWords": context.selection.excluded_words,
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
