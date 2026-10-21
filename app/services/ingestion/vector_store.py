from __future__ import annotations
import json
from pathlib import Path
from typing import Tuple
import numpy as np, faiss
from app.core.config import get_settings
settings = get_settings()
class FaissStore:
    def __init__(self, document_id: str):
        self.base_path = Path(settings.faiss_index_path) / document_id
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.index_path = self.base_path / "index.faiss"
        self.meta_path = self.base_path / "meta.json"
    def save(self, vectors: list[list[float]], metadata: list[dict]) -> None:
        if not vectors: return
        arr = np.array(vectors, dtype="float32")
        index = faiss.IndexFlatIP(arr.shape[1])
        index.add(arr)
        faiss.write_index(index, str(self.index_path))
        self.meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    def load(self):
        if not self.index_path.exists() or not self.meta_path.exists(): return None, []
        return faiss.read_index(str(self.index_path)), json.loads(self.meta_path.read_text(encoding="utf-8"))
    def search(self, query_vector: list[float], top_k: int = 6) -> list[Tuple[int, float]]:
        index, _ = self.load()
        if index is None: return []
        q = np.array([query_vector], dtype="float32")
        scores, ids = index.search(q, top_k)
        return [(int(i), float(s)) for i, s in zip(ids[0], scores[0]) if i != -1]
