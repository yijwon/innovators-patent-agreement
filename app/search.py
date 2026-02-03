from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class PatentRecord:
    patent_id: str
    title: str
    abstract: str
    url: str

    @property
    def content(self) -> str:
        return f"{self.title}\n{self.abstract}"


def load_patents(data_path: Path) -> list[PatentRecord]:
    payload = json.loads(data_path.read_text(encoding="utf-8"))
    return [PatentRecord(**item) for item in payload]


def find_similar_patents(
    query: str,
    patents: Iterable[PatentRecord],
    top_k: int = 5,
) -> list[dict[str, float | str]]:
    patent_list = list(patents)
    corpus = [record.content for record in patent_list]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([query, *corpus])
    query_vector = matrix[0:1]
    patent_vectors = matrix[1:]
    scores = cosine_similarity(query_vector, patent_vectors).flatten()
    ranked = sorted(
        zip(patent_list, scores, strict=True),
        key=lambda item: item[1],
        reverse=True,
    )
    results: list[dict[str, float | str]] = []
    for record, score in ranked[:top_k]:
        results.append(
            {
                "patent_id": record.patent_id,
                "title": record.title,
                "abstract": record.abstract,
                "url": record.url,
                "score": float(score),
            }
        )
    return results
