from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_and_seeded_dashboard_are_ready() -> None:
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    dashboard = client.get("/api/v1/dashboard").json()
    assert dashboard["student"]["streak"] == 17
    assert dashboard["today"]["mission"] == "Graph algorithms"


def test_register_onboarding_and_grounded_tutor_flow() -> None:
    response = client.post("/api/v1/auth/register", json={"email": "arjun-test@example.edu", "password": "learning123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": "Bearer " + token}
    onboarding = client.post("/api/v1/onboarding", headers=headers, json={
        "display_name": "Arjun", "program": "Computer science · Year 2", "subjects": ["DSA"],
        "exam_date": "2026-10-14", "daily_minutes": 120, "learning_style": "examples",
    })
    assert onboarding.status_code == 200
    tutor = client.post("/api/v1/tutor/chat", headers=headers, json={"message": "What about negative edge weights?", "mode": "socratic"})
    assert tutor.status_code == 200
    assert "Bellman" in tutor.json()["answer"]
    assert tutor.json()["citations"][0]["source"].startswith("Graph Theory")


def test_confident_incorrect_answer_is_flagged() -> None:
    auth = client.post("/api/v1/auth/register", json={"email": "quiz-test@example.edu", "password": "learning123"}).json()
    response = client.post("/api/v1/practice/submit", headers={"Authorization": "Bearer " + auth["access_token"]}, json={
        "question_id": "graph-negative-weights", "answer_index": 0, "confidence": 5,
    })
    assert response.status_code == 200
    assert response.json()["correct"] is False
    assert response.json()["confidence_gap"] is True
    assert response.json()["mistake_saved"] is True


def test_practice_question_bank_and_boss_battle_are_consistent() -> None:
    auth = client.post("/api/v1/auth/register", json={"email": "question-bank@example.edu", "password": "learning123"}).json()
    headers = {"Authorization": "Bearer " + auth["access_token"]}
    question_ids = ["graph-negative-weights", "graph-bfs-shortest", "graph-dfs-visited", "graph-bfs-complexity"]
    for question_id in question_ids:
        question = client.get("/api/v1/practice/next", params={"question_id": question_id}, headers=headers)
        assert question.status_code == 200
        payload = question.json()
        assert payload["id"] == question_id
        answer = client.post("/api/v1/practice/submit", headers=headers, json={
            "question_id": question_id,
            "answer_index": payload["answer_index"],
            "confidence": 4,
        })
        assert answer.status_code == 200
        assert answer.json()["correct"] is True
        assert answer.json()["explanation"] == payload["explanation"]

    battle = client.post("/api/v1/assessments/boss-battle", headers=headers)
    assert battle.status_code == 200
    assert battle.json()["question_count"] == 10
    assert len(battle.json()["questions"]) == 10


def test_rejects_unsupported_material_type() -> None:
    auth = client.post("/api/v1/auth/register", json={"email": "upload-test@example.edu", "password": "learning123"}).json()
    response = client.post("/api/v1/materials", headers={"Authorization": "Bearer " + auth["access_token"]}, files={"file": ("notes.exe", b"bad", "application/octet-stream")})
    assert response.status_code == 415


def test_auth_duplicate_and_wrong_password_are_rejected() -> None:
    payload = {"email": "auth-flow@example.edu", "password": "learning123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 200
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409
    assert client.post("/api/v1/auth/login", json={**payload, "password": "wrong-password"}).status_code == 401
    assert client.post("/api/v1/auth/login", json=payload).status_code == 200
    assert client.get("/api/v1/mastery").status_code == 401


def test_demo_upload_grounding_planner_focus_and_wrapped_endpoints() -> None:
    auth = client.post("/api/v1/auth/register", json={"email": "features@example.edu", "password": "learning123"}).json()
    headers = {"Authorization": "Bearer " + auth["access_token"]}
    upload = client.post("/api/v1/materials?subject=DSA", headers=headers, files={"file": ("graphs.txt", b"Breadth-first search finds shortest paths in unweighted graphs.", "text/plain")})
    assert upload.status_code == 201
    assert upload.json()["material"]["characters_extracted"] > 0
    assert any(item["name"] == "graphs.txt" for item in client.get("/api/v1/study-packs", headers=headers).json()["items"])
    answer = client.post("/api/v1/tutor/chat", headers=headers, json={"message": "What does BFS guarantee?", "mode": "learn"})
    assert answer.status_code == 200
    assert answer.json()["grounded"] is True
    assert answer.json()["citations"]
    assert client.get("/api/v1/mastery", headers=headers).status_code == 200
    assert client.get("/api/v1/planner/today").json()["tasks"]
    focus = client.post("/api/v1/focus/complete", headers=headers, json={"topic": "Graph algorithms", "duration_minutes": 25})
    assert focus.status_code == 200
    assert focus.json()["session"]["xp_earned"] == 100
    assert client.get("/api/v1/wrapped").status_code == 200


def test_demo_confidence_mistake_and_flashcard_review_persist() -> None:
    auth = client.post("/api/v1/auth/register", json={"email": "review-flow@example.edu", "password": "learning123"}).json()
    headers = {"Authorization": "Bearer " + auth["access_token"]}
    submitted = client.post("/api/v1/practice/submit", headers=headers, json={
        "question_id": "graph-negative-weights", "answer_index": 0, "confidence": 5,
    })
    assert submitted.json()["confidence_gap"] is True
    mistakes = client.get("/api/v1/mistakes", headers=headers).json()["items"]
    assert len(mistakes) == 1
    assert mistakes[0]["topic"] == "Shortest paths"
    reviewed = client.post(f"/api/v1/mistakes/{mistakes[0]['id']}/review", headers=headers)
    assert reviewed.status_code == 200
    assert client.get("/api/v1/mistakes", headers=headers).json()["items"] == []
    cards = client.get("/api/v1/flashcards/due", headers=headers).json()["items"]
    assert cards[0]["id"] == "demo-card-1"
    response = client.post("/api/v1/flashcards/demo-card-1/review", headers=headers, json={"rating": 4})
    assert response.json()["next_interval_days"] == 3
    assert client.get("/api/v1/flashcards/due", headers=headers).json()["items"] == []
    assert client.post("/api/v1/flashcards/unknown/review", headers=headers, json={"rating": 4}).status_code == 404


def test_demo_study_rooms_create_and_join() -> None:
    auth = client.post("/api/v1/auth/register", json={"email": "room-flow@example.edu", "password": "learning123"}).json()
    headers = {"Authorization": "Bearer " + auth["access_token"]}
    assert client.get("/api/v1/rooms").json()["items"]
    created = client.post("/api/v1/rooms", headers=headers, json={"name": "QA focus room", "subject": "DSA", "capacity": 4, "is_private": False})
    assert created.status_code == 201
    joined = client.post(f"/api/v1/rooms/{created.json()['id']}/join", headers=headers)
    assert joined.status_code == 200
    assert joined.json()["joined"] is True
    assert client.post("/api/v1/rooms/missing/join", headers=headers).status_code == 404
