from __future__ import annotations

from dataclasses import dataclass

from app.core.config import get_settings


@dataclass(frozen=True)
class RetrievedEvidence:
    text: str
    source: str
    score: float


class CandidateRAG:
    """Embedding-backed retrieval boundary.

    The initial implementation uses the OpenAI embeddings API and keeps persistence
    behind a small interface so pgvector can be introduced without changing agents.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.embedding_model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        from openai import AsyncOpenAI

        if not get_settings().openai_api_key:
            return []
        client = AsyncOpenAI(api_key=get_settings().openai_api_key)
        response = await client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    @staticmethod
    def rank_local(query: str, documents: list[tuple[str, str]]) -> list[RetrievedEvidence]:
        query_terms = {x.lower() for x in query.split() if len(x) > 2}
        results: list[RetrievedEvidence] = []
        for text, source in documents:
            terms = {x.lower() for x in text.split() if len(x) > 2}
            score = len(query_terms & terms) / max(1, len(query_terms))
            results.append(RetrievedEvidence(text=text, source=source, score=score))
        return sorted(results, key=lambda item: item.score, reverse=True)
