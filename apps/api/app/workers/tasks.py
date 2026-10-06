import asyncio

from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import KnowledgeChunk
from app.services.documents import split_chunks
from app.workers.celery_app import celery_app
from app.services.ai import embed_texts


@celery_app.task(name="studyverse.prepare_material")
def prepare_material(material_id: str, extracted_text: str) -> dict:
    """Embed and index persisted chunks; safe to retry for the same material."""
    return asyncio.run(_prepare_material(material_id, extracted_text))


async def _prepare_material(material_id: str, extracted_text: str) -> dict:
    chunks = split_chunks(extracted_text)
    if not chunks or not (settings.gemini_api_key or settings.use_vertex_ai) or SessionLocal is None:
        return {"material_id": material_id, "chunk_count": len(chunks), "status": "uploaded"}
    vectors = await embed_texts(chunks)
    async with SessionLocal() as session:
        result = await session.scalars(select(KnowledgeChunk).where(KnowledgeChunk.material_id == material_id).order_by(KnowledgeChunk.chunk_index))
        stored = result.all()
        for row, vector in zip(stored, vectors, strict=False):
            row.embedding = vector
        await session.commit()
    return {"material_id": material_id, "chunk_count": len(chunks), "embedded_count": min(len(stored), len(vectors)), "status": "ready"}
