import asyncio
import json

import httpx

from app.providers.llm import (
    LessonGenerationContext,
    LLMProviderError,
    MockLLMProvider,
    OpenRouterLLMProvider,
)
from app.providers.mock_topic import build_mock_dynamic_topic_plan


def assert_strict_response_schema(node: object) -> None:
    if isinstance(node, dict):
        assert "default" not in node
        properties = node.get("properties")
        if isinstance(properties, dict):
            assert set(node.get("required", [])) == set(properties)
        for child in node.values():
            assert_strict_response_schema(child)
    elif isinstance(node, list):
        for child in node:
            assert_strict_response_schema(child)


def test_openrouter_provider_uses_bearer_auth_and_structured_output() -> None:
    context = LessonGenerationContext(
        cefr_level="B2",
        exam_goal="IELTS reading",
        selected_words=["anchor", "estimate"],
        mastered_words_sample=["stable"],
        tracked_word_count=3400,
    )
    expected = asyncio.run(MockLLMProvider().generate_lesson(context))

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://openrouter.test/api/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.headers["HTTP-Referer"] == "http://localhost:5173"
        payload = json.loads(request.content)
        assert payload["model"] == "provider/test-model"
        context_payload = json.loads(payload["messages"][1]["content"])
        assert "CEFR B2" in payload["messages"][0]["content"]
        assert "between 140 and 180 words" in payload["messages"][0]["content"]
        assert context_payload["readingWordRange"] == {"min": 140, "max": 180}
        assert context_payload["previousValidationErrors"] == []
        assert context_payload["candidateWords"] == ["anchor", "estimate"]
        assert context_payload["anchorWords"] == ["anchor", "estimate"]
        assert context_payload["supportWords"] == []
        assert context_payload["deferredWords"] == []
        assert context_payload["excludedWords"] == []
        assert context_payload["contextWords"] == ["stable"]
        assert context_payload["topicProposal"] is None
        assert context_payload["knowledgeBrief"] is None
        assert context_payload["sourceSnapshotId"] is None
        assert payload["response_format"]["type"] == "json_schema"
        schema = payload["response_format"]["json_schema"]["schema"]
        assert_strict_response_schema(schema)
        assert schema["additionalProperties"] is False
        assert schema["$defs"]["Exercise"]["additionalProperties"] is False
        assert "options" in schema["$defs"]["Exercise"]["required"]
        assert {
            "sourceReference",
            "targetWord",
            "skill",
            "gradingMode",
            "rubric",
        } <= set(schema["$defs"]["Exercise"]["required"])
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(expected.model_dump(mode="json", by_alias=True))
                        }
                    }
                ]
            },
        )

    async def run_request():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            provider = OpenRouterLLMProvider(
                api_key="test-key",
                base_url="https://openrouter.test/api/v1",
                model="provider/test-model",
                http_referer="http://localhost:5173",
                app_title="Lexis",
                client=client,
            )
            return await provider.generate_lesson(context)

    result = asyncio.run(run_request())
    assert result == expected


def test_openrouter_provider_plans_topics_with_structured_language_boundary() -> None:
    expected = build_mock_dynamic_topic_plan(["those", "whole"], "A1")

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload["response_format"]["json_schema"]["name"] == "DynamicTopicPlan"
        schema = payload["response_format"]["json_schema"]["schema"]
        assert_strict_response_schema(schema)
        assert "supportingFacts" in schema["$defs"]["DynamicTopicCandidate"][
            "required"
        ]
        assert "Do not introduce external factual claims" in payload["messages"][0]["content"]
        assert json.loads(payload["messages"][1]["content"]) == {
            "selectedWords": ["those", "whole"],
            "cefrLevel": "A1",
            "examGoal": "CET-4",
        }
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                expected.model_dump(mode="json", by_alias=True)
                            )
                        }
                    }
                ]
            },
        )

    async def run_request():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            provider = OpenRouterLLMProvider(
                api_key="test-key",
                base_url="https://openrouter.test/api/v1",
                model="provider/test-model",
                client=client,
            )
            return await provider.plan_topics(
                selected_words=["those", "whole"],
                cefr_level="A1",
                exam_goal="CET-4",
            )

    result = asyncio.run(run_request())
    assert result == expected


def test_openrouter_provider_rejects_invalid_structured_output() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "not-json"}}]},
        )

    async def run_request() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            provider = OpenRouterLLMProvider(
                api_key="test-key",
                base_url="https://openrouter.test/api/v1",
                model="provider/test-model",
                client=client,
            )
            await provider.summarize_attempt(3, 4, ["anchor"])

    try:
        asyncio.run(run_request())
    except LLMProviderError as error:
        assert str(error) == "OpenRouter returned invalid structured output"
    else:
        raise AssertionError("Expected invalid structured output to fail")
