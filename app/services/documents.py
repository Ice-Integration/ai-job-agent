from __future__ import annotations

import io
from pathlib import Path


def extract_text(filename: str, data: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".txt", ".md", ".json", ".csv"}:
        return data.decode("utf-8", errors="ignore")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError as exc:
            raise RuntimeError("Install pypdf to parse PDF files") from exc
    if suffix == ".docx":
        try:
            from docx import Document
            document = Document(io.BytesIO(data))
            return "\n".join(p.text for p in document.paragraphs)
        except ImportError as exc:
            raise RuntimeError("Install python-docx to parse DOCX files") from exc
    raise ValueError(f"Unsupported document type: {suffix}")


def extract_candidate_signals(text: str) -> dict[str, list[str] | str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    known_skills = [
        "python", "fastapi", "flask", "sql", "postgresql", "mysql", "docker",
        "kubernetes", "aws", "azure", "gcp", "git", "github actions", "pytest",
        "tdd", "microservices", "rest", "graphql", "redis", "linux", "terraform",
        "pandas", "scikit-learn", "openai", "rag", "mcp", "typescript", "react",
    ]
    lowered = text.lower()
    skills = [skill for skill in known_skills if skill in lowered]
    return {"skills": skills, "profile_text": "\n".join(lines)}
