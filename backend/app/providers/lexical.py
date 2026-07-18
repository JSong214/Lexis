from typing import Protocol

from app.schemas.topic import WordSemanticProfile, WordSense


class LexicalSource(Protocol):
    name: str
    version: str

    def enrich(self, words: list[str]) -> tuple[list[WordSemanticProfile], list[str]]: ...


def _profile(
    word: str,
    difficulty: str,
    *senses: WordSense,
) -> WordSemanticProfile:
    return WordSemanticProfile(
        word=word,
        lemma=word,
        difficulty=difficulty,
        senses=list(senses),
        source_name="lexis-fixture",
        source_version="2026-07-17-v1",
    )


def _sense(
    sense_id: str,
    definition: str,
    meaning_zh: str,
    part_of_speech: str,
    *,
    collocations: tuple[str, ...] = (),
    domains: tuple[str, ...] = (),
) -> WordSense:
    return WordSense(
        id=sense_id,
        definition=definition,
        meaning_zh=meaning_zh,
        part_of_speech=part_of_speech,
        collocations=list(collocations),
        semantic_domains=list(domains),
    )


FIXTURE_PROFILES = {
    profile.word: profile
    for profile in (
        _profile(
            "anchor",
            "B2",
            _sense(
                "anchor.reference_point",
                "a fact or idea used as a starting reference",
                "参照点；基准",
                "noun",
                collocations=("use as an anchor", "initial anchor"),
                domains=("judgment", "decision-making"),
            ),
            _sense(
                "anchor.secure_object",
                "a heavy object used to keep a boat in place",
                "锚",
                "noun",
                collocations=("drop anchor", "raise anchor"),
                domains=("navigation",),
            ),
        ),
        _profile(
            "estimate",
            "B1",
            _sense(
                "estimate.approximate_judgment",
                "an approximate calculation or judgment based on available information",
                "估计；估算",
                "noun",
                collocations=("make an estimate", "rough estimate"),
                domains=("measurement", "decision-making"),
            ),
        ),
        _profile(
            "ambiguous",
            "C1",
            _sense(
                "ambiguous.open_to_interpretation",
                "having more than one possible meaning or lacking a clear answer",
                "含糊的；有歧义的",
                "adjective",
                collocations=("ambiguous wording", "remain ambiguous"),
                domains=("language", "uncertainty"),
            ),
        ),
        _profile(
            "criteria",
            "B2",
            _sense(
                "criteria.judging_standards",
                "standards used to judge or decide something",
                "标准；准则",
                "noun",
                collocations=("clear criteria", "selection criteria"),
                domains=("evaluation", "decision-making"),
            ),
        ),
        _profile(
            "validate",
            "C1",
            _sense(
                "validate.check_soundness",
                "to check that a claim, method, or result is sound",
                "验证；确认有效",
                "verb",
                collocations=("validate a result", "validate an assumption"),
                domains=("evidence", "evaluation"),
            ),
        ),
        _profile(
            "review",
            "A2",
            _sense(
                "review.study_again",
                "to study information again so that it can be remembered",
                "复习",
                "verb",
                collocations=("review notes", "review regularly"),
                domains=("learning",),
            ),
        ),
        _profile(
            "reinforce",
            "B2",
            _sense(
                "reinforce.make_stronger",
                "to make an idea, skill, or habit stronger",
                "巩固；加强",
                "verb",
                collocations=("reinforce learning", "reinforce a habit"),
                domains=("learning", "behavior"),
            ),
        ),
        _profile(
            "apply",
            "B1",
            _sense(
                "apply.use_in_situation",
                "to use knowledge or a method in a particular situation",
                "应用；运用",
                "verb",
                collocations=("apply knowledge", "apply a rule"),
                domains=("learning", "problem-solving"),
            ),
        ),
        _profile(
            "retain",
            "B2",
            _sense(
                "retain.keep_in_memory",
                "to keep information in memory",
                "记住；保留",
                "verb",
                collocations=("retain information", "retain knowledge"),
                domains=("memory", "learning"),
            ),
        ),
        _profile(
            "segment",
            "B2",
            _sense(
                "segment.part_of_whole",
                "one part of a larger whole",
                "部分；分段",
                "noun",
                collocations=("market segment", "text segment"),
                domains=("structure", "analysis"),
            ),
        ),
        _profile(
            "scope",
            "B2",
            _sense(
                "scope.covered_range",
                "the range of work or information that is included",
                "范围",
                "noun",
                collocations=("project scope", "within scope"),
                domains=("planning",),
            ),
        ),
        _profile(
            "draft",
            "B1",
            _sense(
                "draft.early_version",
                "an early version that is expected to be revised",
                "草稿；初稿",
                "noun",
                collocations=("first draft", "revise a draft"),
                domains=("writing", "iteration"),
            ),
        ),
        _profile(
            "compile",
            "B2",
            _sense(
                "compile.collect_material",
                "to collect information from several places into one work",
                "汇编；整理",
                "verb",
                collocations=("compile notes", "compile a report"),
                domains=("information", "writing"),
            ),
        ),
    )
}


class FixtureLexicalSource:
    name = "lexis-fixture"
    version = "2026-07-17-v1"

    def enrich(self, words: list[str]) -> tuple[list[WordSemanticProfile], list[str]]:
        profiles: list[WordSemanticProfile] = []
        unmatched: list[str] = []
        seen: set[str] = set()
        for word in words:
            key = word.strip().casefold()
            if not key or key in seen:
                continue
            seen.add(key)
            profile = FIXTURE_PROFILES.get(key)
            if profile is None:
                unmatched.append(word.strip())
            else:
                profiles.append(profile)
        return profiles, unmatched


def get_lexical_source() -> LexicalSource:
    return FixtureLexicalSource()
