import asyncio

from fastapi.testclient import TestClient

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
                    mastered_word_count=3400,
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
        json={"cefrLevel": "B2", "examGoal": "IELTS reading"},
    )

    assert response.status_code == 409, response.text


def test_generate_and_read_valid_context_lesson(client: TestClient) -> None:
    register_and_sync(client)

    response = client.post(
        "/api/v1/lessons/generate",
        json={
            "cefrLevel": "B2",
            "examGoal": "IELTS reading",
            "selectedWords": ["anchor", "estimate", "ambiguous"],
        },
    )

    assert response.status_code == 200
    lesson = response.json()
    assert lesson["status"] == "valid"
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


def test_submit_answer_saves_immediate_feedback(client: TestClient) -> None:
    register_and_sync(client)
    lesson = client.post(
        "/api/v1/lessons/generate",
        json={
            "cefrLevel": "B2",
            "examGoal": "IELTS reading",
            "selectedWords": ["anchor", "estimate"],
        },
    ).json()

    correct = client.post(
        f"/api/v1/lessons/{lesson['id']}/answers",
        json={"exerciseIndex": 0, "answer": "A reference point"},
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
    lesson = client.post(
        "/api/v1/lessons/generate",
        json={
            "cefrLevel": "B2",
            "examGoal": "IELTS reading",
            "selectedWords": ["anchor", "estimate"],
        },
    ).json()
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
    lesson = client.post(
        "/api/v1/lessons/generate",
        json={
            "cefrLevel": "B2",
            "examGoal": "IELTS reading",
            "selectedWords": ["anchor", "estimate"],
        },
    ).json()

    incomplete = client.post(f"/api/v1/lessons/{lesson['id']}/complete")
    assert incomplete.status_code == 409

    answers = [
        "A reference point",
        "The second idea",
        "To make reasoning visible",
        "I use an anchor when I estimate the project.",
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
    assert {item["word"] for item in payload["masteryUpdates"]} == {
        "anchor",
        "estimate",
    }
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
