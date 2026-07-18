import asyncio
from uuid import UUID

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app
from app.models import ContextLesson
from app.providers.llm import LessonGenerationContext, MockLLMProvider
from app.services.lesson_validation import CEFR_WORD_RANGES, count_words, validate_context_lesson


def register_and_sync(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "lesson@example.com", "password": "correct-horse-battery"},
    )
    assert response.status_code == 201
    assert (
        client.put(
            "/api/v1/maimemo/connection",
            json={"provider": "mock"},
        ).status_code
        == 200
    )
    assert client.post("/api/v1/maimemo/sync").status_code == 200


DEFAULT_CANDIDATE_WORDS = [
    "anchor",
    "estimate",
    "ambiguous",
    "criteria",
    "validate",
]


def generate_lesson(
    client: TestClient,
    selected_words: list[str] | None = None,
):
    candidates = selected_words or DEFAULT_CANDIDATE_WORDS
    proposal_response = client.post(
        "/api/v1/lessons/topic-proposals",
        json={
            "cefrLevel": "B2",
            "examGoal": "IELTS reading",
            "selectedWords": candidates,
        },
    )
    assert proposal_response.status_code == 200, proposal_response.text
    proposal = proposal_response.json()["proposals"][0]
    anchor_words = [usage["word"] for usage in proposal["wordUsages"] if usage["role"] == "anchor"]
    response = client.post(
        "/api/v1/lessons/generate",
        json={
            "cefrLevel": "B2",
            "examGoal": "IELTS reading",
            "selectedWords": candidates,
            "proposalId": proposal["id"],
            "anchorWords": anchor_words,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()

async def downgrade_lesson_to_v1(lesson_id: str) -> None:
    override_get_db = app.dependency_overrides[get_db]
    async for db in override_get_db():
        lesson = await db.get(ContextLesson, UUID(lesson_id))
        assert lesson is not None

        legacy_keys = (
            "title",
            "readingText",
            "unfamiliarWords",
            "targetWords",
            "grammarAnalysis",
            "exercises",
        )
        legacy_content = {key: lesson.content[key] for key in legacy_keys}
        legacy_exercise_keys = (
            "type",
            "question",
            "options",
            "expectedAnswer",
            "explanationZh",
        )
        legacy_content["exercises"] = [
            {key: exercise[key] for key in legacy_exercise_keys}
            for exercise in lesson.content["exercises"]
        ]
        lesson.content = legacy_content
        metadata = dict(lesson.generation_metadata)
        metadata.pop("schema_version", None)
        lesson.generation_metadata = metadata
        await db.commit()
        return

    raise AssertionError("Test database session was unavailable")


def test_mock_provider_satisfies_all_cefr_ranges() -> None:
    provider = MockLLMProvider()

    for level, (minimum, maximum) in CEFR_WORD_RANGES.items():
        content = asyncio.run(
            provider.generate_lesson(
                LessonGenerationContext(
                    cefr_level=level,
                    exam_goal="General English",
                    selected_words=["anchor", "estimate"],
                    mastered_words_sample=["stable"],
                    tracked_word_count=3400,
                )
            )
        )
        assert minimum <= count_words(content.reading_text) <= maximum
        assert validate_context_lesson(content, level) == []


def test_generation_requires_vocabulary_profile(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "no-profile@example.com", "password": "correct-horse-battery"},
    )
    assert response.status_code == 201

    response = client.post(
        "/api/v1/lessons/generate",
        json={
            "cefrLevel": "B2",
            "examGoal": "IELTS reading",
            "selectedWords": DEFAULT_CANDIDATE_WORDS,
            "proposalId": "missing-proposal",
            "anchorWords": ["anchor", "estimate", "ambiguous"],
        },
    )

    assert response.status_code == 409, response.text


def test_generate_and_read_valid_context_lesson(client: TestClient) -> None:
    register_and_sync(client)

    lesson = generate_lesson(client)
    assert lesson["status"] == "valid"
    metadata = lesson["generationMetadata"]
    assert metadata["provider"] == "mock"
    assert metadata["model"] == "mock"
    assert metadata["prompt_version"] == "knowledge-lesson-generation-v1"
    assert metadata["schema_version"] == "context-lesson-v2"
    assert lesson["content"]["targetWords"] == ["anchor", "estimate", "ambiguous"]
    assert "expectedAnswer" not in lesson["content"]["exercises"][0]
    assert "explanationZh" not in lesson["content"]["exercises"][0]
    assert {item["type"] for item in lesson["content"]["exercises"]} == {
        "vocabulary_context",
        "syntax",
        "paragraph_logic",
        "output",
    }
    detail = client.get(f"/api/v1/lessons/{lesson['id']}")
    assert detail.status_code == 200
    assert detail.json()["id"] == lesson["id"]

def test_legacy_and_current_lessons_share_history_and_learning_flow(
    client: TestClient,
) -> None:
    register_and_sync(client)
    legacy_lesson = generate_lesson(client)
    asyncio.run(downgrade_lesson_to_v1(legacy_lesson["id"]))
    current_lesson = generate_lesson(client)

    legacy_detail = client.get(f"/api/v1/lessons/{legacy_lesson['id']}")
    assert legacy_detail.status_code == 200, legacy_detail.text
    legacy_payload = legacy_detail.json()
    assert legacy_payload["content"]["title"] == legacy_lesson["content"]["title"]
    assert legacy_payload["content"]["topicId"].startswith("legacy-")
    assert legacy_payload["content"]["knowledgeSources"] == []

    exercises = legacy_payload["content"]["exercises"]
    for index, exercise in enumerate(exercises):
        answer = (
            exercise["options"][0]
            if exercise["options"]
            else "I use an anchor when I estimate the project."
        )
        response = client.post(
            f"/api/v1/lessons/{legacy_lesson['id']}/answers",
            json={"exerciseIndex": index, "answer": answer},
        )
        assert response.status_code == 201, response.text

    completed = client.post(f"/api/v1/lessons/{legacy_lesson['id']}/complete")
    assert completed.status_code == 200, completed.text

    history = client.get("/api/v1/lessons")
    assert history.status_code == 200, history.text
    history_by_id = {item["id"]: item for item in history.json()}
    assert set(history_by_id) == {legacy_lesson["id"], current_lesson["id"]}
    assert history_by_id[legacy_lesson["id"]]["attemptStatus"] == "completed"
    assert history_by_id[legacy_lesson["id"]]["exerciseCount"] == len(exercises)
    assert history_by_id[current_lesson["id"]]["title"] == current_lesson["content"]["title"]


def test_arbitrary_selected_words_use_language_topic_fallback(
    client: TestClient,
) -> None:
    register_and_sync(client)
    candidates = ["segment", "draft"]

    proposal_response = client.post(
        "/api/v1/lessons/topic-proposals",
        json={
            "cefrLevel": "B2",
            "examGoal": "General English",
            "selectedWords": candidates,
        },
    )

    assert proposal_response.status_code == 200, proposal_response.text
    proposal_payload = proposal_response.json()
    assert proposal_payload["planningMode"] == "language_fallback"
    assert len(proposal_payload["proposals"]) == 2
    proposal = proposal_payload["proposals"][0]
    anchor_words = [
        usage["word"]
        for usage in proposal["wordUsages"]
        if usage["role"] == "anchor"
    ]
    assert len(anchor_words) == 1
    assert set(proposal["deferredWords"]) == set(candidates) - set(anchor_words)

    lesson_response = client.post(
        "/api/v1/lessons/generate",
        json={
            "cefrLevel": "B2",
            "examGoal": "General English",
            "selectedWords": candidates,
            "proposalId": proposal["id"],
            "anchorWords": anchor_words,
        },
    )

    assert lesson_response.status_code == 200, lesson_response.text
    lesson = lesson_response.json()
    assert lesson["status"] == "valid"
    assert lesson["content"]["targetWords"] == anchor_words
    assert {
        profile["word"]
        for profile in lesson["generationMetadata"]["word_semantic_profiles"]
    } == set(candidates)


def test_submit_answer_saves_immediate_feedback(client: TestClient) -> None:
    register_and_sync(client)
    lesson = generate_lesson(client)

    correct = client.post(
        f"/api/v1/lessons/{lesson['id']}/answers",
        json={"exerciseIndex": 0, "answer": lesson["content"]["exercises"][0]["options"][0]},
    )
    assert correct.status_code == 201
    assert correct.json()["isCorrect"] is True
    assert correct.json()["feedbackText"].startswith("回答正确")

    revised = client.post(
        f"/api/v1/lessons/{lesson['id']}/answers",
        json={"exerciseIndex": 0, "answer": "A final answer"},
    )
    assert revised.status_code == 201
    assert revised.json()["id"] == correct.json()["id"]
    assert revised.json()["isCorrect"] is False

    attempt = client.get(f"/api/v1/lessons/{lesson['id']}/attempt")
    assert attempt.status_code == 200
    assert attempt.json()["status"] == "draft"
    assert len(attempt.json()["feedback"]) == 1
    assert attempt.json()["feedback"][0]["answer"] == "A final answer"


def test_lesson_attempt_is_isolated_by_user(client: TestClient) -> None:
    register_and_sync(client)
    lesson = generate_lesson(client)
    assert (
        client.post(
            f"/api/v1/lessons/{lesson['id']}/answers",
            json={"exerciseIndex": 0, "answer": "A reference point"},
        ).status_code
        == 201
    )

    assert client.post("/api/v1/auth/logout").status_code == 204
    assert (
        client.post(
            "/api/v1/auth/register",
            json={"email": "other@example.com", "password": "correct-horse-battery"},
        ).status_code
        == 201
    )

    assert client.get("/api/v1/lessons").json() == []
    assert client.get(f"/api/v1/lessons/{lesson['id']}").status_code == 404
    assert client.get(f"/api/v1/lessons/{lesson['id']}/attempt").status_code == 404
    assert (
        client.post(
            f"/api/v1/lessons/{lesson['id']}/answers",
            json={"exerciseIndex": 0, "answer": "A reference point"},
        ).status_code
        == 404
    )


def test_complete_lesson_saves_summary_and_mastery(client: TestClient) -> None:
    register_and_sync(client)
    lesson = generate_lesson(client)

    incomplete = client.post(f"/api/v1/lessons/{lesson['id']}/complete")
    assert incomplete.status_code == 409

    answers = [
        exercise["options"][0]
        if exercise["options"]
        else "I use an anchor when I estimate the project."
        for exercise in lesson["content"]["exercises"]
    ]
    for index, answer in enumerate(answers):
        response = client.post(
            f"/api/v1/lessons/{lesson['id']}/answers",
            json={"exerciseIndex": index, "answer": answer},
        )
        assert response.status_code == 201
        assert response.json()["isCorrect"] is True

    completed = client.post(f"/api/v1/lessons/{lesson['id']}/complete")
    assert completed.status_code == 200
    payload = completed.json()
    assert payload["attempt"]["status"] == "completed"
    assert payload["attempt"]["completedAt"] is not None
    assert "4 道练习" in payload["attempt"]["finalSummary"]
    assert {item["word"] for item in payload["masteryUpdates"]} == set(
        lesson["content"]["targetWords"]
    )
    assert all(item["exposureCount"] == 1 for item in payload["masteryUpdates"])

    repeated = client.post(f"/api/v1/lessons/{lesson['id']}/complete")
    assert repeated.status_code == 200
    assert all(item["exposureCount"] == 1 for item in repeated.json()["masteryUpdates"])

    saved = client.get(f"/api/v1/lessons/{lesson['id']}/completion")
    assert saved.status_code == 200
    assert saved.json()["attempt"]["finalSummary"] == payload["attempt"]["finalSummary"]

    history = client.get("/api/v1/lessons")
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["id"] == lesson["id"]
    assert history.json()[0]["attemptStatus"] == "completed"
    assert history.json()[0]["answeredCount"] == 4
    assert history.json()[0]["correctCount"] == 4


def test_practice_words_can_become_anchor_words(client: TestClient) -> None:
    register_and_sync(client)
    lesson = generate_lesson(
        client,
        ["review", "reinforce", "apply", "retain"],
    )
    assert "review" in lesson["content"]["targetWords"]
