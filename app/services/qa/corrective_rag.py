from __future__ import annotations
from dataclasses import dataclass
from app.services.qa.retriever import RetrievedChunk
@dataclass
class CorrectiveDecision:
    supported: bool; confidence: float; issues: list[str]; revised_query: str; final_answer: str | None = None
def build_context(chunks: list[RetrievedChunk]) -> str:
    return " ".join([f"[chunk_id={c.chunk_id} | page={c.page_number} | hybrid={c.hybrid_score:.3f}] {c.text}" for c in chunks])
def basic_groundedness_heuristic(answer: str, chunks: list[RetrievedChunk]) -> CorrectiveDecision:
    context = build_context(chunks).lower(); ans = answer.lower().strip()
    if not chunks: return CorrectiveDecision(False, 0.0, ["No supporting chunks were retrieved."], revised_query="")
    if any(x in ans for x in ["i could not find", "not mentioned", "not enough information"]): return CorrectiveDecision(False, 0.98, [], revised_query="")
    keywords = [w for w in ans.split() if len(w) > 5][:10]
    overlap = sum(1 for w in keywords if w in context)
    confidence = min(0.95, 0.45 + overlap / 20)
    supported = overlap >= max(2, len(keywords) // 5)
    issues = [] if supported else ["Low lexical overlap between draft answer and retrieved context."]
    return CorrectiveDecision(supported, confidence, issues, revised_query="")
