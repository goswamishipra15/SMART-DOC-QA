from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from docx import Document as DocxDocument
from pypdf import PdfReader

from app.utils.text_cleaning import normalize_whitespace


def extract_pdf_text(path: str) -> List[Dict[str, Any]]:
    reader = PdfReader(path)
    pages: List[Dict[str, Any]] = []

    for i, page in enumerate(reader.pages, start=1):
        text = normalize_whitespace(page.extract_text() or "")

        if text:
            pages.append({
                "page_number": i,
                "text": text
            })

    return pages


def extract_docx_text(path: str) -> List[Dict[str, Any]]:
    doc = DocxDocument(path)

    paragraphs = []

    for p in doc.paragraphs:
        cleaned = normalize_whitespace(p.text)

        if cleaned:
            paragraphs.append(cleaned)

    full_text = "\n".join(paragraphs)

    if not full_text:
        return []

    return [{
        "page_number": None,
        "text": full_text
    }]


def extract_document(path: str) -> List[Dict[str, Any]]:
    suffix = Path(path).suffix.lower()

    if suffix == ".pdf":
        return extract_pdf_text(path)

    if suffix == ".docx":
        return extract_docx_text(path)

    raise ValueError(f"Unsupported file type: {suffix}")