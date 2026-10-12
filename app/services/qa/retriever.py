from __future__ import annotations
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.db.models.chunk import DocumentChunk
from app.services.ingestion.embeddings import embed_texts
from app.services.ingestion.vector_store import FaissStore
from app.services.ingestion.bm25_store import BM25Store
@dataclass
class RetrievedChunk:
    chunk_id: str; page_number: int | None; text: str; dense_score: float; sparse_score: float; hybrid_score: float
class HybridRetriever:
    def __init__(self, db: Session, document_id: str, top_k: int = 6): self.db = db; self.document_id = document_id; self.top_k = top_k
    def _load_chunks(self) -> list[DocumentChunk]: return self.db.query(DocumentChunk).filter(DocumentChunk.document_id == self.document_id).order_by(DocumentChunk.chunk_index.asc()).all()
    def retrieve(self, query: str) -> list[RetrievedChunk]:
        chunks = self._load_chunks()
        if not chunks: return []
        texts = [c.chunk_text for c in chunks]
        query_vector = embed_texts([query])[0]
        dense_hits = FaissStore(self.document_id).search(query_vector, top_k=self.top_k * 2)
        dense_map = {idx: score for idx, score in dense_hits}
        bm25_hits = BM25Store(self.document_id).search(query, [{"chunk_text": t} for t in texts], top_k=self.top_k * 2)
        bm25_map = {idx: score for idx, score in bm25_hits}
        def norm(scores: dict[int, float]) -> dict[int, float]:
            if not scores: return {}
            values = list(scores.values())
            mn, mx = min(values), max(values)
            if mx == mn: return {k: 1.0 for k in scores}
            return {k: (v - mn) / (mx - mn) for k, v in scores.items()}
        dense_n = norm(dense_map); sparse_n = norm(bm25_map)
        ranked = []
        for idx, chunk in enumerate(chunks):
            d = dense_n.get(idx, 0.0); s = sparse_n.get(idx, 0.0); hybrid = 0.65 * d + 0.35 * s
            if hybrid > 0:
                ranked.append(RetrievedChunk(chunk_id=chunk.id, page_number=chunk.page_number, text=chunk.chunk_text, dense_score=d, sparse_score=s, hybrid_score=hybrid))
        ranked.sort(key=lambda x: x.hybrid_score, reverse=True)
        return ranked[: self.top_k]
