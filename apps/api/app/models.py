from datetime import datetime
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "students"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(80), default="Learner")
    program: Mapped[str] = mapped_column(String(120), default="")
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class StudyMaterial(Base):
    __tablename__ = "study_materials"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(120), default="Unsorted")
    mime_type: Mapped[str] = mapped_column(String(160))
    storage_uri: Mapped[str] = mapped_column(Text)
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    material_id: Mapped[str] = mapped_column(ForeignKey("study_materials.id", ondelete="CASCADE"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class TopicMastery(Base):
    __tablename__ = "topic_mastery"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    topic: Mapped[str] = mapped_column(String(160))
    mastery: Mapped[float] = mapped_column(Float, default=0)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MistakeRecord(Base):
    __tablename__ = "mistake_records"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    topic: Mapped[str] = mapped_column(String(160))
    question: Mapped[str] = mapped_column(Text)
    student_answer: Mapped[str] = mapped_column(Text)
    correct_answer: Mapped[str] = mapped_column(Text)
    confidence: Mapped[int] = mapped_column(Integer)
    misconception: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Flashcard(Base):
    __tablename__ = "flashcards"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    front: Mapped[str] = mapped_column(Text)
    back: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(255), default="")
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
