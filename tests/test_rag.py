from app.services.rag import CandidateRAG, chunk_text


def test_chunk_text_preserves_all_content() -> None:
    text = "A" * 3000
    chunks = chunk_text(text, size=1000, overlap=100)
    assert chunks
    assert "".join([chunks[0][:1000], chunks[1][100:]])[:1000] == "A" * 1000


def test_local_rag_ranking() -> None:
    results = CandidateRAG.rank_local(
        "python fastapi",
        [("Python FastAPI PostgreSQL", "cv"), ("Java Spring", "other")],
    )
    assert results[0].source == "cv"
    assert results[0].score > results[1].score
