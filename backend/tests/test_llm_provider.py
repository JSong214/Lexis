import asyncio
import json

import httpx

from app.providers.llm import (
    LessonGenerationContext,
    LLMProviderError,
    MockLLMProvider,
    OpenRouterLLMProvider,
)


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
        assert payload["response_format"]["type"] == "json_schema"
        schema = payload["response_format"]["json_schema"]["schema"]
        assert schema["additionalProperties"] is False
        assert schema["$defs"]["Exercise"]["additionalProperties"] is False
        assert "options" in schema["$defs"]["Exercise"]["required"]
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
