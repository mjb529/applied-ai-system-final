"""Lightweight retrieval layer for the Game Glitch Investigator.

The project intentionally avoids a paid API dependency so the final system is
reproducible for graders. Retrieval is lexical, transparent, and deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


DEFAULT_KNOWLEDGE_DIR = Path(__file__).parent / "knowledge_base"


@dataclass(frozen=True)
class KnowledgeChunk:
    """A small source passage used as evidence for a diagnosis."""

    source: str
    title: str
    tags: tuple[str, ...]
    content: str


@dataclass(frozen=True)
class RetrievedEvidence:
    """A scored retrieval result."""

    chunk: KnowledgeChunk
    score: float
    matched_terms: tuple[str, ...]


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())


def _unique_tokens(text: str) -> set[str]:
    return set(_tokenize(text))


def load_knowledge_base(directory: Path | str = DEFAULT_KNOWLEDGE_DIR) -> list[KnowledgeChunk]:
    """Load markdown knowledge chunks from a directory.

    Each ``##`` heading starts a new chunk. A line beginning with ``Tags:`` is
    parsed as metadata and included in retrieval scoring.
    """

    directory = Path(directory)
    chunks: list[KnowledgeChunk] = []

    for path in sorted(directory.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        sections = re.split(r"(?m)^##\s+", text)

        for section in sections:
            section = section.strip()
            if not section:
                continue

            lines = section.splitlines()
            title = lines[0].strip("# ").strip()
            body_lines = lines[1:]
            tags: tuple[str, ...] = ()

            if body_lines and body_lines[0].lower().startswith("tags:"):
                tag_text = body_lines[0].split(":", 1)[1]
                tags = tuple(tag.strip().lower() for tag in tag_text.split(",") if tag.strip())
                body_lines = body_lines[1:]

            content = "\n".join(body_lines).strip()
            if content:
                chunks.append(
                    KnowledgeChunk(
                        source=path.name,
                        title=title,
                        tags=tags,
                        content=content,
                    )
                )

    return chunks


class KnowledgeRetriever:
    """Retrieve relevant debugging knowledge for a bug report."""

    def __init__(self, chunks: list[KnowledgeChunk] | None = None) -> None:
        self.chunks = chunks if chunks is not None else load_knowledge_base()

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedEvidence]:
        query_terms = _unique_tokens(query)
        if not query_terms:
            return []

        results: list[RetrievedEvidence] = []

        for chunk in self.chunks:
            content_terms = _unique_tokens(" ".join([chunk.title, *chunk.tags, chunk.content]))
            matches = query_terms.intersection(content_terms)
            if not matches:
                continue

            title_terms = _unique_tokens(chunk.title)
            tag_terms = set(chunk.tags)
            title_bonus = len(query_terms.intersection(title_terms)) * 1.5
            tag_bonus = len(query_terms.intersection(tag_terms)) * 2.0
            phrase_bonus = self._phrase_bonus(query, chunk.content)
            normalized_overlap = len(matches) / max(len(query_terms), 1)
            score = normalized_overlap + title_bonus + tag_bonus + phrase_bonus

            results.append(
                RetrievedEvidence(
                    chunk=chunk,
                    score=round(score, 3),
                    matched_terms=tuple(sorted(matches)),
                )
            )

        return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]

    @staticmethod
    def _phrase_bonus(query: str, content: str) -> float:
        query_lower = query.lower()
        content_lower = content.lower()
        phrases = [
            "secret number",
            "session state",
            "new game",
            "too high",
            "too low",
            "out of range",
            "attempts left",
            "high score",
        ]
        return sum(0.5 for phrase in phrases if phrase in query_lower and phrase in content_lower)
