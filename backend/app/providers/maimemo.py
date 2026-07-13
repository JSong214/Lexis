from dataclasses import dataclass
from typing import Protocol

import httpx

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class MaimemoSyncResult:
    new_words: list[str]
    fuzzy_words: list[str]
    practice_words: list[str]
    mastered_words_sample: list[str]
    tracked_word_count: int
    daily_finished_count: int = 0
    daily_total_count: int = 0
    daily_study_time_ms: int = 0


class MaimemoProviderError(RuntimeError):
    pass


class MaimemoSyncProvider(Protocol):
    name: str

    async def sync(self, token: str | None = None) -> MaimemoSyncResult: ...


class MockMaimemoSyncProvider:
    name = "mock"

    async def sync(self, token: str | None = None) -> MaimemoSyncResult:
        return MaimemoSyncResult(
            new_words=["anchor", "segment", "estimate", "criteria", "draft", "validate"],
            fuzzy_words=["retain", "compile", "ambiguous", "scope"],
            practice_words=["review", "reinforce", "apply"],
            mastered_words_sample=["stable", "fluent", "pattern", "contrast"],
            tracked_word_count=3400,
            daily_finished_count=18,
            daily_total_count=30,
            daily_study_time_ms=1_080_000,
        )


def unique_spellings(items: list[object]) -> list[str]:
    words: list[str] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        spelling = item.get("voc_spelling")
        if not isinstance(spelling, str):
            continue
        normalized = spelling.strip()
        key = normalized.casefold()
        if normalized and key not in seen:
            seen.add(key)
            words.append(normalized)
    return words


class RealMaimemoSyncProvider:
    name = "maimemo"

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.client = client

    async def _post(
        self,
        path: str,
        token: str,
        payload: dict[str, object],
    ) -> dict[str, object]:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        try:
            if self.client is not None:
                response = await self.client.post(
                    f"{self.base_url}/{path}",
                    headers=headers,
                    json=payload,
                )
            else:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.post(
                        f"{self.base_url}/{path}",
                        headers=headers,
                        json=payload,
                    )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as error:
            if error.response.status_code in {401, 403}:
                raise MaimemoProviderError("Maimemo token was rejected") from error
            raise MaimemoProviderError(
                f"Maimemo returned HTTP {error.response.status_code}"
            ) from error
        except httpx.RequestError as error:
            raise MaimemoProviderError("Maimemo request failed") from error
        except ValueError as error:
            raise MaimemoProviderError("Maimemo returned invalid JSON") from error

        if not isinstance(data, dict):
            raise MaimemoProviderError("Maimemo returned an unexpected response")
        if data.get("success") is False:
            raise MaimemoProviderError("Maimemo reported a request error")
        wrapped_data = data.get("data")
        if isinstance(wrapped_data, dict):
            return wrapped_data
        return data

    async def sync(self, token: str | None = None) -> MaimemoSyncResult:
        if not token:
            raise MaimemoProviderError("Maimemo token is required")

        today_payload = await self._post(
            "study/get_today_items",
            token,
            {"limit": 1000},
        )
        progress_payload = await self._post(
            "study/get_study_progress",
            token,
            {},
        )
        records_payload = await self._post(
            "study/query_study_records",
            token,
            {"limit": 1000},
        )
        count_payload = await self._post(
            "study/query_study_records",
            token,
            {"as_count": True},
        )

        today_items = today_payload.get("today_items")
        records = records_payload.get("records")
        tracked_count = count_payload.get("count")
        progress = progress_payload.get("progress")
        if not isinstance(today_items, list) or not isinstance(records, list):
            raise MaimemoProviderError("Maimemo study data is incomplete")
        if not isinstance(tracked_count, int) or tracked_count < 0:
            raise MaimemoProviderError("Maimemo tracked word count is unavailable")
        if not isinstance(progress, dict):
            raise MaimemoProviderError("Maimemo study progress is unavailable")
        daily_finished_count = progress.get("finished")
        daily_total_count = progress.get("total")
        daily_study_time_ms = progress.get("study_time")
        if not all(
            isinstance(value, int) and value >= 0
            for value in (
                daily_finished_count,
                daily_total_count,
                daily_study_time_ms,
            )
        ):
            raise MaimemoProviderError("Maimemo study progress is invalid")

        new_words = unique_spellings(
            [item for item in today_items if isinstance(item, dict) and item.get("is_new") is True]
        )
        fuzzy_candidates = unique_spellings(
            [
                item
                for item in today_items
                if isinstance(item, dict)
                and item.get("first_response") in {"VAGUE", "FORGET"}
            ]
            + [
                record
                for record in records
                if isinstance(record, dict)
                and (
                    record.get("tags") == "STICKING"
                    or record.get("last_response") in {"VAGUE", "FORGET"}
                )
            ]
        )
        new_word_keys = {word.casefold() for word in new_words}
        fuzzy_words = [
            word for word in fuzzy_candidates if word.casefold() not in new_word_keys
        ][:50]
        fuzzy_word_keys = {word.casefold() for word in fuzzy_candidates}
        practice_words = [
            word
            for word in unique_spellings(today_items)
            if word.casefold() not in new_word_keys
            and word.casefold() not in fuzzy_word_keys
        ][:50]
        mastered_words_sample = unique_spellings(
            [
                record
                for record in records
                if isinstance(record, dict)
                and (
                    record.get("tags") == "WELL_FAMILIAR"
                    or record.get("last_response") == "WELL_FAMILIAR"
                )
            ]
        )[:50]

        return MaimemoSyncResult(
            new_words=new_words,
            fuzzy_words=fuzzy_words,
            practice_words=practice_words,
            mastered_words_sample=mastered_words_sample,
            tracked_word_count=tracked_count,
            daily_finished_count=daily_finished_count,
            daily_total_count=daily_total_count,
            daily_study_time_ms=daily_study_time_ms,
        )


def build_maimemo_sync_provider(
    provider_name: str,
    settings: Settings | None = None,
) -> MaimemoSyncProvider:
    if provider_name == "mock":
        return MockMaimemoSyncProvider()
    if provider_name == "maimemo":
        current_settings = settings or get_settings()
        return RealMaimemoSyncProvider(
            base_url=current_settings.maimemo_base_url,
            timeout_seconds=current_settings.maimemo_timeout_seconds,
        )
    raise MaimemoProviderError(f"Unsupported Maimemo provider: {provider_name}")
