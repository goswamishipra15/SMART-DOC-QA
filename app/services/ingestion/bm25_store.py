from __future__ import annotations
import json, re
from pathlib import Path
from typing import Tuple
from rank_bm25 import BM25Okapi
from app.core.config import get_settings
settings = get_settings()
def tokenize(text: str) -> list[str]: return re.findall(r"[A-Za-z0-9_]+", text.lower())
class BM25Store:
    def __init__(self, document_id: str):
        self.base_path = Path(settings.bm25_index_path) / document_id
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.corpus_path = self.base_path / "corpus.json"
    def save(self, chunks: list[dict]) -> None:
        corpus = [tokenize(chunk["chunk_text"]) for chunk in chunks]
        self.corpus_path.write_text(json.dumps(corpus, indent=2), encoding="utf-8")
    def search(self, query: str, chunks: list[dict], top_k: int = 6) -> list[Tuple[int, float]]:
        corpus = [tokenize(chunk["chunk_text"]) for chunk in chunks]
        if not corpus: return []
        bm25 = BM25Okapi(corpus)
        scores = bm25.get_scores(tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [(idx, float(score)) for idx, score in ranked]
