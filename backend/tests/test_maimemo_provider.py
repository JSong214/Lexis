import asyncio
import json

import httpx

from app.providers.maimemo import MaimemoProviderError, RealMaimemoSyncProvider


def test_real_maimemo_provider_normalizes_read_only_study_data() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        assert request.headers["Authorization"] == "Bearer test-token"
        payload = json.loads(request.content)
        if request.url.path.endswith("/study/get_today_items"):
            assert payload == {"limit": 1000}
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "errors": [],
                    "data": {
                        "today_items": [
                            {
                                "voc_spelling": "anchor",
                                "is_new": True,
                                "first_response": "VAGUE",
                            },
                            {"voc_spelling": "estimate", "is_new": True},
                            {
                                "voc_spelling": "retain",
                                "is_new": False,
                                "first_response": "VAGUE",
                            },
                            {
                                "voc_spelling": "review",
                                "is_new": False,
                                "first_response": "FAMILIAR",
                            },
                        ]
                    },
                },
            )
        if request.url.path.endswith("/study/get_study_progress"):
            assert payload == {}
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "errors": [],
                    "data": {
                        "progress": {
                            "finished": 12,
                            "total": 30,
                            "study_time": 720_000,
                        }
                    },
                },
            )
        if payload == {"limit": 1000}:
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "errors": [],
                    "data": {
                        "records": [
                            {
                                "voc_spelling": "stable",
                                "tags": "WELL_FAMILIAR",
                                "last_response": "FAMILIAR",
                            },
                            {
                                "voc_spelling": "fluent",
                                "tags": "STICKING",
                                "last_response": "WELL_FAMILIAR",
                            },
                            {
                                "voc_spelling": "ambiguous",
                                "tags": "STICKING",
                                "last_response": "VAGUE",
                            },
                        ],
                        "count": 0,
                    },
                },
            )
        assert payload == {"as_count": True}
        return httpx.Response(
            200,
            json={
                "success": True,
                "errors": [],
                "data": {"records": [], "count": 123},
            },
        )

    async def run_sync():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            provider = RealMaimemoSyncProvider(
                base_url="https://open.maimemo.test/open/api/v1",
                timeout_seconds=10,
                client=client,
            )
            return await provider.sync("test-token")

    result = asyncio.run(run_sync())

    assert result.new_words == ["anchor", "estimate"]
    assert result.fuzzy_words == ["retain", "fluent", "ambiguous"]
    assert result.mastered_words_sample == ["stable", "fluent"]
    assert result.tracked_word_count == 123
    assert result.daily_finished_count == 12
    assert result.daily_total_count == 30
    assert result.daily_study_time_ms == 720_000
    assert calls == [
        "/open/api/v1/study/get_today_items",
        "/open/api/v1/study/get_study_progress",
        "/open/api/v1/study/query_study_records",
        "/open/api/v1/study/query_study_records",
    ]


def test_real_maimemo_provider_reports_rejected_token() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "unauthorized"})

    async def run_sync() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            provider = RealMaimemoSyncProvider(
                base_url="https://open.maimemo.test/open/api/v1",
                timeout_seconds=10,
                client=client,
            )
            await provider.sync("bad-token")

    try:
        asyncio.run(run_sync())
    except MaimemoProviderError as error:
        assert str(error) == "Maimemo token was rejected"
    else:
        raise AssertionError("Expected rejected token to fail")
