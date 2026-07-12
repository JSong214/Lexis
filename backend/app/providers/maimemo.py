from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class MaimemoSyncResult:
    new_words: list[str]
    fuzzy_words: list[str]
    mastered_words_sample: list[str]
    mastered_word_count: int


class MaimemoSyncProvider(Protocol):
    async def sync(self) -> MaimemoSyncResult: ...


class MockMaimemoSyncProvider:
    async def sync(self) -> MaimemoSyncResult:
        return MaimemoSyncResult(
            new_words=["anchor", "segment", "estimate", "criteria", "draft", "validate"],
            fuzzy_words=["retain", "compile", "ambiguous", "scope"],
            mastered_words_sample=["stable", "fluent", "pattern", "contrast"],
            mastered_word_count=3400,
        )


def get_maimemo_sync_provider() -> MaimemoSyncProvider:
    return MockMaimemoSyncProvider()
