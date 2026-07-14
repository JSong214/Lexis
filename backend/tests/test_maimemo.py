from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from app.core.secret_cipher import SecretCipher


def register(client: TestClient, email: str = "sync@example.com") -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correct-horse-battery"},
    )
    assert response.status_code == 201


def test_secret_cipher_encrypts_and_decrypts() -> None:
    cipher = SecretCipher(Fernet.generate_key().decode("utf-8"))

    encrypted = cipher.encrypt("maimemo-secret")

    assert encrypted != "maimemo-secret"
    assert cipher.decrypt(encrypted) == "maimemo-secret"


def test_sync_requires_connection(client: TestClient) -> None:
    register(client)

    response = client.post("/api/v1/maimemo/sync")

    assert response.status_code == 409
    assert response.json() == {"detail": "Configure Maimemo before syncing"}


def test_mock_sync_builds_vocabulary_profile(client: TestClient) -> None:
    register(client)
    connection = client.put(
        "/api/v1/maimemo/connection",
        json={"provider": "mock", "secret": "maimemo-secret"},
    )
    assert connection.status_code == 200
    assert connection.json()["configured"] is True
    assert connection.json()["secretSaved"] is True
    assert "secret" not in connection.json()

    response = client.post("/api/v1/maimemo/sync")

    assert response.status_code == 200
    profile = response.json()
    assert profile["newWords"] == [
        "anchor",
        "segment",
        "estimate",
        "criteria",
        "draft",
        "validate",
    ]
    assert profile["fuzzyWords"] == ["retain", "compile", "ambiguous", "scope"]
    assert profile["practiceWords"] == ["review", "reinforce", "apply"]
    assert profile["masteredWordsSample"] == ["stable", "fluent", "pattern", "contrast"]
    assert profile["trackedWordCount"] == 3400
    assert profile["dailyFinishedCount"] == 18
    assert profile["dailyTotalCount"] == 30
    assert profile["dailyStudyTimeMs"] == 1_080_000
    assert profile["snapshotWords"] == [
        {"word": "anchor", "sourceCategory": "new"},
        {"word": "segment", "sourceCategory": "new"},
        {"word": "estimate", "sourceCategory": "new"},
        {"word": "criteria", "sourceCategory": "new"},
        {"word": "draft", "sourceCategory": "new"},
        {"word": "validate", "sourceCategory": "new"},
        {"word": "retain", "sourceCategory": "fuzzy"},
        {"word": "compile", "sourceCategory": "fuzzy"},
        {"word": "ambiguous", "sourceCategory": "fuzzy"},
        {"word": "scope", "sourceCategory": "fuzzy"},
        {"word": "review", "sourceCategory": "practice"},
        {"word": "reinforce", "sourceCategory": "practice"},
        {"word": "apply", "sourceCategory": "practice"},
        {"word": "stable", "sourceCategory": "mastered_sample"},
        {"word": "fluent", "sourceCategory": "mastered_sample"},
        {"word": "pattern", "sourceCategory": "mastered_sample"},
        {"word": "contrast", "sourceCategory": "mastered_sample"},
    ]

    latest = client.get("/api/v1/vocabulary/profile")
    assert latest.status_code == 200
    assert latest.json()["snapshotId"] == profile["snapshotId"]
    latest_words = sorted(
        latest.json()["snapshotWords"],
        key=lambda item: (item["sourceCategory"], item["word"]),
    )
    synced_words = sorted(
        profile["snapshotWords"],
        key=lambda item: (item["sourceCategory"], item["word"]),
    )
    assert latest_words == synced_words


def test_profile_is_isolated_by_user(client: TestClient) -> None:
    register(client, "first-sync@example.com")
    client.put("/api/v1/maimemo/connection", json={"provider": "mock"})
    first_profile = client.post("/api/v1/maimemo/sync")
    assert first_profile.status_code == 200
    client.post("/api/v1/auth/logout")

    register(client, "second-sync@example.com")
    response = client.get("/api/v1/vocabulary/profile")

    assert response.status_code == 404
    assert response.json() == {"detail": "No vocabulary profile is available"}


def test_real_connection_requires_saved_token(client: TestClient) -> None:
    register(client, "real-sync@example.com")

    connection = client.put(
        "/api/v1/maimemo/connection",
        json={"provider": "maimemo"},
    )

    assert connection.status_code == 200
    assert connection.json()["configured"] is False
    assert connection.json()["provider"] == "maimemo"
    sync = client.post("/api/v1/maimemo/sync")
    assert sync.status_code == 409
    assert sync.json() == {"detail": "Save a Maimemo token before syncing"}
