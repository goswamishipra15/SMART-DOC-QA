from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
from app.core.config import get_settings
settings = get_settings()
@dataclass
class Chunk:
    chunk_index: int; page_number: int | None; text: str; token_count: int

def _simple_token_count(text: str) -> int: return max(1, len(text.split()))

def chunk_pages(pages: List[Dict[str, Any]], chunk_size: int | None = None, overlap: int | None = None) -> List[Chunk]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    chunks: List[Chunk] = []
    chunk_index = 0
    for page in pages:
        text = page["text"]
        page_number = page.get("page_number")
        paragraphs = [p.strip() for p in text.split(" ") if p.strip()]
        current = ""
        for para in paragraphs:
            candidate = (current + " " + para).strip() if current else para
            if len(candidate) <= chunk_size:
                current = candidate; continue
            if current:
                chunks.append(Chunk(chunk_index, page_number, current, _simple_token_count(current))); chunk_index += 1
            start = 0
            while start < len(para):
                end = min(len(para), start + chunk_size)
                window = para[start:end].strip()
                if window:
                    chunks.append(Chunk(chunk_index, page_number, window, _simple_token_count(window))); chunk_index += 1
                if end == len(para): break
                start = max(0, end - overlap)
            current = ""
        if current:
            chunks.append(Chunk(chunk_index, page_number, current, _simple_token_count(current))); chunk_index += 1
    return chunks
