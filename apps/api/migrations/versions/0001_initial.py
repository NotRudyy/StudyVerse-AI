"""Initial StudyVerse schema: students, materials, chunks, mastery."""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "students",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(80), nullable=False, server_default="Learner"),
        sa.Column("program", sa.String(120), nullable=False, server_default=""),
        sa.Column("preferences", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_students_email", "students", ["email"], unique=True)
    op.create_table(
        "study_materials",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True),
        sa.Column("student_id", sa.UUID(as_uuid=False), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("subject", sa.String(120), nullable=False, server_default="Unsorted"),
        sa.Column("mime_type", sa.String(160), nullable=False),
        sa.Column("storage_uri", sa.Text(), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_study_materials_student_id", "study_materials", ["student_id"])
    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True),
        sa.Column("material_id", sa.UUID(as_uuid=False), sa.ForeignKey("study_materials.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
    )
    op.create_index("ix_knowledge_chunks_material_id", "knowledge_chunks", ["material_id"])
    op.execute("CREATE INDEX ix_knowledge_chunks_embedding_hnsw ON knowledge_chunks USING hnsw (embedding vector_cosine_ops) WHERE embedding IS NOT NULL")
    op.create_table(
        "topic_mastery",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True),
        sa.Column("student_id", sa.UUID(as_uuid=False), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic", sa.String(160), nullable=False),
        sa.Column("mastery", sa.Float(), nullable=False, server_default="0"),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("student_id", "topic", name="uq_topic_mastery_student_topic"),
    )
    op.create_index("ix_topic_mastery_student_id", "topic_mastery", ["student_id"])
    op.create_table(
        "mistake_records",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True),
        sa.Column("student_id", sa.UUID(as_uuid=False), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic", sa.String(160), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("student_answer", sa.Text(), nullable=False),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("misconception", sa.Text(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_mistake_records_student_id", "mistake_records", ["student_id"])
    op.create_table(
        "flashcards",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True),
        sa.Column("student_id", sa.UUID(as_uuid=False), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("front", sa.Text(), nullable=False),
        sa.Column("back", sa.Text(), nullable=False),
        sa.Column("source", sa.String(255), nullable=False, server_default=""),
        sa.Column("ease_factor", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("due_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_flashcards_student_id", "flashcards", ["student_id"])
    op.create_index("ix_flashcards_due_at", "flashcards", ["due_at"])


def downgrade() -> None:
    op.drop_index("ix_knowledge_chunks_embedding_hnsw", table_name="knowledge_chunks")
    op.drop_table("flashcards")
    op.drop_table("mistake_records")
    op.drop_table("topic_mastery")
    op.drop_table("knowledge_chunks")
    op.drop_table("study_materials")
    op.drop_table("students")
