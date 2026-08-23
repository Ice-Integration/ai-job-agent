from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.infrastructure.tables import CandidateChunkRecord


@dataclass(frozen=True)
class RetrievedEvidence:
    text: str
    source: str
    score: float


def chunk_text(text: str, size: int = 1200, overlap: int = 150) -> list[str]:
    clean = " ".join(text.split())
    if not clean:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = min(start + size, len(clean))
        chunks.append(clean[start:end])
        if end == len(clean):
            break
        start = max(end - overlap, start + 1)
    return chunks


class CandidateRAG:
    def __init__(self) -> None:
        self.model = get_settings().embedding_model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        from openai import AsyncOpenAI

        settings = get_settings()
        if not settings.openai_api_key or not texts:
            return []
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    async def index(self, session: AsyncSession, candidate_id: UUID, text: str) -> int:
        chunks = chunk_text(text)
        embeddings = await self.embed(chunks)
        if not embeddings:
            return 0
        session.add_all(
            CandidateChunkRecord(
                id=uuid4(), candidate_id=candidate_id, content=content,
                embedding=embedding, chunk_metadata={"type": "candidate_profile"}
            )
            for content, embedding in zip(chunks, embeddings, strict=True)
        )
        await session.commit()
        return len(chunks)

    async def search(self, session: AsyncSession, candidate_id: UUID, query: str, limit: int = 8) -> list[RetrievedEvidence]:
        embeddings = await self.embed([query])
        if not embeddings:
            return []
        distance = CandidateChunkRecord.embedding.cosine_distance(embeddings[0])
        result = await session.execute(
            select(CandidateChunkRecord.content)
            .where(CandidateChunkRecord.candidate_id == candidate_id)
            .order_by(distance)
            .limit(limit)
        )
        return [RetrievedEvidence(text=text, source="candidate_knowledge_base", score=1.0) for text in result.scalars()]

    @staticmethod
    def rank_local(query: str, documents: list[tuple[str, str]]) -> list[RetrievedEvidence]:
        query_terms = {x.lower() for x in query.split() if len(x) > 2}
        results: list[RetrievedEvidence] = []
        for text, source in documents:
            terms = {x.lower() for x in text.split() if len(x) > 2}
            score = len(query_terms & terms) / max(1, len(query_terms))
            results.append(RetrievedEvidence(text=text, source=source, score=score))
        return sorted(results, key=lambda item: item.score, reverse=True)
