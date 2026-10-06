from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.demo_data import DASHBOARD, DEMO_QUESTION, DEMO_QUESTIONS
from app.models import KnowledgeChunk, Student, StudyMaterial, TopicMastery
from app.models import Flashcard, MistakeRecord
from app.schemas import AuthInput, ChatInput, FlashcardReview, FocusSessionInput, OnboardingInput, QuizSubmission, RoomInput
from app.services.ai import ai_is_configured, embed_texts, generate_answer
from app.services.documents import extract_text, split_chunks
from app.services.rag import retrieve
from app.services.storage import store_upload

API_PREFIX = "/api/v1"
ALGORITHM = "HS256"
pwd_hasher = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)
demo_users: dict[str, dict] = {}
demo_materials: list[dict] = []
demo_sessions: list[dict] = []
demo_mistakes: list[dict] = []
demo_flashcard_reviews: dict[str, datetime] = {}
demo_rooms = [
    {"id": "room-dsa", "name": "DSA accountability room", "subject": "Data structures & algorithms", "people": 4, "capacity": 6, "tags": ["Quiet focus", "Exam prep"]},
    {"id": "room-cs", "name": "Late-night CS crew", "subject": "Computer science", "people": 8, "capacity": 10, "tags": ["Lo-fi", "Chill pace"]},
]

app = FastAPI(
    title="StudyVerse AI API",
    description="A student-centered learning API for study packs, grounded tutoring, adaptive practice, mastery, and focus.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


def _make_token(user_id: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(hours=12)
    return jwt.encode({"sub": user_id, "exp": expires}, settings.jwt_secret, algorithm=ALGORITHM)


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession | None = Depends(get_session),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to continue")
    try:
        user_id = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[ALGORITHM]).get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your session expired") from exc
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    if session:
        student = await session.get(Student, user_id)
        if student:
            return {"id": student.id, "email": student.email, "name": student.display_name}
    user = next((item for item in demo_users.values() if item["id"] == user_id), None)
    if user:
        return {"id": user["id"], "email": user["email"], "name": user.get("name", "Learner")}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Student account not found")


@app.get(API_PREFIX + "/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok", "service": "studyverse-api", "demo_mode": settings.demo_mode, "ai_configured": ai_is_configured()}


@app.post(API_PREFIX + "/auth/register", tags=["auth"])
async def register(payload: AuthInput, session: AsyncSession | None = Depends(get_session)) -> dict:
    email = payload.email.lower()
    if session:
        existing = await session.scalar(select(Student).where(Student.email == email))
        if existing:
            raise HTTPException(status_code=409, detail="An account with this email already exists")
        student = Student(email=email, password_hash=pwd_hasher.hash(payload.password))
        session.add(student)
        await session.commit()
        user_id = student.id
    else:
        if email in demo_users:
            raise HTTPException(status_code=409, detail="An account with this email already exists")
        user_id = str(uuid4())
        demo_users[email] = {"id": user_id, "email": email, "password_hash": pwd_hasher.hash(payload.password), "name": "Learner"}
    return {"access_token": _make_token(user_id), "token_type": "bearer", "user": {"id": user_id, "email": email}, "demo_mode": settings.demo_mode}


@app.post(API_PREFIX + "/auth/login", tags=["auth"])
async def login(payload: AuthInput, session: AsyncSession | None = Depends(get_session)) -> dict:
    email = payload.email.lower()
    user = None
    if session:
        student = await session.scalar(select(Student).where(Student.email == email))
        if student and pwd_hasher.verify(payload.password, student.password_hash):
            user = {"id": student.id, "email": student.email, "name": student.display_name}
    else:
        record = demo_users.get(email)
        if record and pwd_hasher.verify(payload.password, record["password_hash"]):
            user = {"id": record["id"], "email": email, "name": record["name"]}
    if not user:
        raise HTTPException(status_code=401, detail="Email or password didn't match")
    return {"access_token": _make_token(user["id"]), "token_type": "bearer", "user": user, "demo_mode": settings.demo_mode}


@app.post(API_PREFIX + "/onboarding", tags=["auth"])
async def save_onboarding(payload: OnboardingInput, user: dict = Depends(current_user), session: AsyncSession | None = Depends(get_session)) -> dict:
    if session:
        student = await session.get(Student, user["id"])
        if student:
            student.display_name = payload.display_name
            student.program = payload.program
            student.preferences = {"subjects": payload.subjects, "exam_date": str(payload.exam_date) if payload.exam_date else None, "daily_minutes": payload.daily_minutes, "learning_style": payload.learning_style}
            await session.commit()
    else:
        for record in demo_users.values():
            if record["id"] == user["id"]:
                record.update(name=payload.display_name, program=payload.program, preferences=payload.model_dump(mode="json"))
                break
    return {"saved": True, "plan": {"study_minutes_per_day": payload.daily_minutes, "subjects": payload.subjects, "next_step": "Start a short diagnostic to calibrate your topic mastery."}}


@app.get(API_PREFIX + "/dashboard", tags=["learning"])
async def dashboard() -> dict:
    return deepcopy(DASHBOARD)


@app.get(API_PREFIX + "/study-packs", tags=["materials"])
async def study_packs(user: dict = Depends(current_user)) -> dict:
    owned = [row for row in demo_materials if row.get("student_id") == user["id"]]
    return {"items": deepcopy(DASHBOARD["study_packs"]) + [{"id": row["id"], "name": row["filename"], "subject": row["subject"], "chapters": 1, "cards": 12, "progress": 0} for row in owned]}


@app.post(API_PREFIX + "/materials", status_code=201, tags=["materials"])
async def upload_material(
    file: UploadFile = File(...),
    subject: str = "Unsorted",
    user: dict = Depends(current_user),
    session: AsyncSession | None = Depends(get_session),
) -> dict:
    allowed = {"pdf", "pptx", "docx", "png", "jpg", "jpeg", "webp", "txt", "md"}
    filename = Path(file.filename or "study-material").name
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix not in allowed:
        raise HTTPException(status_code=415, detail="Upload a PDF, PPTX, DOCX, image, TXT, or Markdown file")
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="This file is over the 20 MB demo limit")
    try:
        text = extract_text(filename, content)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="This file could not be read. Try exporting it as PDF or DOCX.") from exc
    storage_uri = store_upload(filename, content, user["id"])
    material_id = str(uuid4())
    chunks = split_chunks(text)
    if session:
        material = StudyMaterial(id=material_id, student_id=user["id"], filename=filename, subject=subject, mime_type=file.content_type or "application/octet-stream", storage_uri=storage_uri, extracted_text=text)
        session.add(material)
        session.add_all([KnowledgeChunk(material_id=material_id, chunk_index=index, content=chunk) for index, chunk in enumerate(chunks)])
        await session.commit()
    row = {"id": material_id, "student_id": user["id"], "filename": filename, "subject": subject, "storage_uri": storage_uri, "extracted_text": text, "characters_extracted": len(text), "chunks_created": len(chunks), "status": "ready" if text and settings.demo_mode else "processing" if chunks else "uploaded"}
    demo_materials.append(row)
    if chunks and not settings.demo_mode:
        from app.workers.tasks import prepare_material

        prepare_material.delay(material_id, text)
    return {"material": row, "studypack": {"summary": "Your material is ready for Nova to teach from.", "flashcards_generated": 12, "quiz_questions_generated": 8}}


@app.post(API_PREFIX + "/tutor/chat", tags=["tutor"])
async def tutor_chat(payload: ChatInput, user: dict = Depends(current_user), session: AsyncSession | None = Depends(get_session)) -> dict:
    owned_materials = [row for row in demo_materials if row.get("student_id") == user["id"]]
    context = []
    if session and ai_is_configured():
        query_vectors = await embed_texts([payload.message])
        if query_vectors:
            distance = KnowledgeChunk.embedding.cosine_distance(query_vectors[0])
            result = await session.execute(
                select(KnowledgeChunk, StudyMaterial, distance.label("distance"))
                .join(StudyMaterial, StudyMaterial.id == KnowledgeChunk.material_id)
                .where(StudyMaterial.student_id == user["id"], KnowledgeChunk.embedding.is_not(None))
                .order_by(distance)
                .limit(3)
            )
            context = [{"text": chunk.content, "citation": material.filename + (", p. " + str(chunk.page_number) if chunk.page_number else ""), "score": max(0.0, 1.0 - float(score))} for chunk, material, score in result.all()]
    if not context:
        context = retrieve(payload.message, extra_materials=owned_materials)
    answer = await generate_answer(payload.message, context, payload.mode)
    return {"answer": answer, "mode": payload.mode, "citations": [{"source": row["citation"], "excerpt": row["text"][:240], "score": row["score"]} for row in context], "grounded": bool(context), "demo_mode": settings.demo_mode}


@app.get(API_PREFIX + "/practice/next", tags=["practice"])
async def next_question(question_id: str | None = None, topic: str = "Graph algorithms", user: dict = Depends(current_user)) -> dict:
    question = next((row for row in DEMO_QUESTIONS if row["id"] == question_id), DEMO_QUESTION)
    return {**deepcopy(question), "topic": question["topic"] or topic, "difficulty": "medium", "points": 45}


@app.post(API_PREFIX + "/practice/submit", tags=["practice"])
async def submit_answer(payload: QuizSubmission, user: dict = Depends(current_user), session: AsyncSession | None = Depends(get_session)) -> dict:
    question = next((row for row in DEMO_QUESTIONS if row["id"] == payload.question_id), None)
    if question is None:
        raise HTTPException(status_code=404, detail="Practice question not found")
    if payload.answer_index >= len(question["choices"]):
        raise HTTPException(status_code=422, detail="Choose one of the available answers")
    topic = question["topic"]
    correct = payload.answer_index == question["answer_index"]
    confidence_gap = not correct and payload.confidence >= 4
    if session:
        current = await session.scalar(select(TopicMastery).where(TopicMastery.student_id == user["id"], TopicMastery.topic == topic))
        if current:
            current.mastery = min(100, current.mastery + (1 if correct else 0))
            current.evidence_count += 1
        else:
            session.add(TopicMastery(student_id=user["id"], topic=topic, mastery=47 if correct else 46, evidence_count=1))
        await session.commit()
    if confidence_gap and session:
        session.add(MistakeRecord(student_id=user["id"], topic=topic, question=question["prompt"], student_answer=question["choices"][payload.answer_index], correct_answer=question["choices"][question["answer_index"]], confidence=payload.confidence, misconception=f"Confident answer needs another look: {topic.lower()}.", status="open"))
        await session.commit()
    elif confidence_gap:
        demo_mistakes.append({
            "id": str(uuid4()), "student_id": user["id"], "topic": topic,
            "question": question["prompt"], "student_answer": question["choices"][payload.answer_index],
            "correct_answer": question["choices"][question["answer_index"]], "confidence": payload.confidence,
            "misconception": f"Confident answer needs another look: {topic.lower()}.", "status": "open",
        })
    return {"correct": correct, "explanation": question["explanation"], "xp_earned": 45 if correct else 0, "confidence_gap": confidence_gap, "mastery_updated": True, "mistake_saved": confidence_gap}


@app.get(API_PREFIX + "/mistakes", tags=["practice"])
async def list_mistakes(user: dict = Depends(current_user), session: AsyncSession | None = Depends(get_session)) -> dict:
    if not session:
        return {"items": [{key: value for key, value in row.items() if key != "student_id"} for row in demo_mistakes if row["student_id"] == user["id"] and row["status"] == "open"]}
    result = await session.scalars(select(MistakeRecord).where(MistakeRecord.student_id == user["id"], MistakeRecord.status == "open").order_by(MistakeRecord.created_at.desc()))
    return {"items": [{"id": row.id, "topic": row.topic, "question": row.question, "student_answer": row.student_answer, "correct_answer": row.correct_answer, "confidence": row.confidence, "misconception": row.misconception, "status": row.status} for row in result.all()]}


@app.post(API_PREFIX + "/mistakes/{mistake_id}/review", tags=["practice"])
async def review_mistake(mistake_id: str, user: dict = Depends(current_user), session: AsyncSession | None = Depends(get_session)) -> dict:
    if not session:
        mistake = next((row for row in demo_mistakes if row["id"] == mistake_id and row["student_id"] == user["id"] and row["status"] == "open"), None)
        if not mistake:
            raise HTTPException(status_code=404, detail="Mistake not found")
        mistake["status"] = "reviewed"
        return {"reviewed": True, "xp_earned": 30}
    mistake = await session.scalar(select(MistakeRecord).where(MistakeRecord.id == mistake_id, MistakeRecord.student_id == user["id"]))
    if not mistake:
        raise HTTPException(status_code=404, detail="Mistake not found")
    mistake.status = "reviewed"
    await session.commit()
    return {"reviewed": True, "xp_earned": 30}


@app.get(API_PREFIX + "/flashcards/due", tags=["practice"])
async def due_flashcards(user: dict = Depends(current_user), session: AsyncSession | None = Depends(get_session)) -> dict:
    if not session:
        card = {"id": "demo-card-1", "front": "What does BFS guarantee on an unweighted graph?", "back": "A shortest path by number of edges.", "source": "Graph Theory · p. 8"}
        due_at = demo_flashcard_reviews.get(f"{user['id']}:{card['id']}")
        return {"items": [card] if due_at is None or due_at <= datetime.now(timezone.utc) else []}
    now = datetime.now(timezone.utc)
    result = await session.scalars(select(Flashcard).where(Flashcard.student_id == user["id"], Flashcard.due_at <= now).order_by(Flashcard.due_at).limit(30))
    return {"items": [{"id": row.id, "front": row.front, "back": row.back, "source": row.source} for row in result.all()]}


@app.post(API_PREFIX + "/flashcards/{card_id}/review", tags=["practice"])
async def review_flashcard(card_id: str, payload: FlashcardReview, user: dict = Depends(current_user), session: AsyncSession | None = Depends(get_session)) -> dict:
    if not session:
        if card_id != "demo-card-1":
            raise HTTPException(status_code=404, detail="Flashcard not found")
        interval = 1 if payload.rating < 3 else 3
        demo_flashcard_reviews[f"{user['id']}:{card_id}"] = datetime.now(timezone.utc) + timedelta(days=interval)
        return {"reviewed": True, "next_interval_days": interval}
    card = await session.scalar(select(Flashcard).where(Flashcard.id == card_id, Flashcard.student_id == user["id"]))
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    if payload.rating < 3:
        card.interval_days = 1
    elif card.review_count == 0:
        card.interval_days = 1
    elif card.review_count == 1:
        card.interval_days = 6
    else:
        card.interval_days = max(1, round(card.interval_days * card.ease_factor))
    card.ease_factor = max(1.3, card.ease_factor + 0.1 - (5 - payload.rating) * (0.08 + (5 - payload.rating) * 0.02))
    card.review_count += 1
    card.due_at = datetime.now(timezone.utc) + timedelta(days=card.interval_days)
    await session.commit()
    return {"reviewed": True, "next_interval_days": card.interval_days}


@app.get(API_PREFIX + "/mastery", tags=["learning"])
async def mastery_map(user: dict = Depends(current_user)) -> dict:
    return {"overall": DASHBOARD["mastery"], "topics": deepcopy(DASHBOARD["topics"]), "prerequisites": [{"from": "Recursion", "to": "Graph algorithms", "reason": "DFS uses recursive traversal"}, {"from": "Recursion", "to": "Backtracking", "reason": "State restoration follows recursive calls"}]}


@app.get(API_PREFIX + "/planner/today", tags=["planner"])
async def today_plan() -> dict:
    return {"date": datetime.now(timezone.utc).date().isoformat(), "exam_countdown_days": 12, "tasks": [{"time": "6:00 PM", "title": "Graph traversal sprint", "duration_minutes": 42, "kind": "mission", "completed": False}, {"time": "6:45 PM", "title": "Explain recursion to Nova", "duration_minutes": 15, "kind": "teach-back", "completed": False}, {"time": "7:05 PM", "title": "Review five flashcards", "duration_minutes": 10, "kind": "spaced-repetition", "completed": False}]}


@app.post(API_PREFIX + "/focus/complete", tags=["focus"])
async def complete_focus(payload: FocusSessionInput, user: dict = Depends(current_user)) -> dict:
    session_row = {"id": str(uuid4()), "topic": payload.topic, "duration_minutes": payload.duration_minutes, "xp_earned": payload.duration_minutes * 4, "completed_at": datetime.now(timezone.utc).isoformat()}
    demo_sessions.append(session_row)
    return {"session": session_row, "streak": 18, "message": "Focus session complete. Your progress is updated."}


@app.get(API_PREFIX + "/wrapped", tags=["analytics"])
async def study_wrapped() -> dict:
    return {"period": "2026-09-26/2026-10-02", "focus_minutes": 402, "days_active": 5, "xp_earned": 1840, "mastery_change": 6, "mistakes_repaired": 4, "top_topics": [{"name": "Trees & traversals", "mastery": 83}, {"name": "Database normalization", "mastery": 76}, {"name": "Graph algorithms", "mastery": 64}]}


@app.post(API_PREFIX + "/assessments/boss-battle", tags=["practice"])
async def boss_battle(user: dict = Depends(current_user)) -> dict:
    questions = [deepcopy(DEMO_QUESTIONS[index % len(DEMO_QUESTIONS)]) for index in range(10)]
    return {"id": str(uuid4()), "name": "Graph Guardian", "topic": "Graph algorithms", "question_count": len(questions), "duration_minutes": 25, "points": 500, "questions": questions}


@app.get(API_PREFIX + "/rooms", tags=["social"])
async def list_rooms() -> dict:
    return {"items": deepcopy(demo_rooms)}


@app.post(API_PREFIX + "/rooms", status_code=201, tags=["social"])
async def create_room(payload: RoomInput, user: dict = Depends(current_user)) -> dict:
    room = {"id": str(uuid4()), "name": payload.name, "subject": payload.subject, "people": 1, "capacity": payload.capacity, "is_private": payload.is_private, "host_id": user["id"], "tags": ["New room"]}
    demo_rooms.append(room)
    return room


@app.post(API_PREFIX + "/rooms/{room_id}/join", tags=["social"])
async def join_room(room_id: str, user: dict = Depends(current_user)) -> dict:
    room = next((item for item in demo_rooms if item["id"] == room_id), None)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room["people"] >= room["capacity"]:
        raise HTTPException(status_code=409, detail="This room is full")
    room["people"] += 1
    return {"joined": True, "room": room, "student_id": user["id"]}
