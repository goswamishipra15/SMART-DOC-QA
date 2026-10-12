# Smart Document Q&A System

Production-style Retrieval-Augmented Generation (RAG) API for document question answering using:

- FastAPI
- LangChain
- LangGraph
- Groq LLM
- FAISS
- BM25 Hybrid Retrieval
- Corrective RAG
- PostgreSQL
- Redis
- Celery
- Docker Compose

---

# Overview

This project is a scalable document question-answering backend where users can:

- Upload PDF/DOCX documents
- Ask natural language questions
- Get grounded answers from document content
- Continue multi-turn conversations
- Use async ingestion for large documents
- Reduce hallucinations using Corrective RAG

The system is designed as a production-oriented B2B SaaS architecture with modular services, background processing, retrieval validation, and hybrid search.

---

# Features

## Document Upload & Processing

- PDF and DOCX support
- Async ingestion pipeline using Celery
- Chunking with overlap
- Metadata-aware indexing

## Hybrid Retrieval

- Dense vector search using FAISS
- Sparse keyword retrieval using BM25
- Hybrid score fusion

## Corrective RAG

- Groundedness verification
- Retry retrieval if answer confidence is low
- Prevent hallucinated responses

## Conversational Q&A

- Multi-turn conversation support
- Query rewriting using LangGraph
- Conversation memory stored in PostgreSQL

## Infrastructure

- Docker Compose setup
- PostgreSQL persistence
- Redis task queue
- Flower monitoring
- HuggingFace model caching

---

# Architecture

```text
                ┌──────────────────┐
                │     FastAPI      │
                └────────┬─────────┘
                         │
                         ▼
               ┌──────────────────┐
               │ PostgreSQL DB    │
               │ Conversations    │
               │ Documents        │
               │ Chunks           │
               └──────────────────┘
                         │
                         ▼
               ┌──────────────────┐
               │ Celery Worker    │
               │ Async Ingestion  │
               └──────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
┌──────────────────┐           ┌──────────────────┐
│ SentenceTransform│           │ BM25 Retriever   │
│ Embeddings       │           │ Sparse Search    │
└──────────────────┘           └──────────────────┘
        ▼
┌──────────────────┐
│ FAISS Vector DB  │
└──────────────────┘
        ▼
┌──────────────────┐
│ LangGraph Flow   │
│ Corrective RAG   │
└──────────────────┘
        ▼
┌──────────────────┐
│ Groq LLM         │
└──────────────────┘
```

---

# Tech Stack

| Layer                  | Technology           |
| ---------------------- | -------------------- |
| API                    | FastAPI              |
| Workflow Orchestration | LangGraph            |
| LLM Framework          | LangChain            |
| LLM Provider           | Groq                 |
| Embeddings             | SentenceTransformers |
| Vector Search          | FAISS                |
| Sparse Retrieval       | BM25                 |
| Database               | PostgreSQL           |
| ORM                    | SQLAlchemy           |
| Migrations             | Alembic              |
| Background Tasks       | Celery               |
| Queue Broker           | Redis                |
| Containerization       | Docker Compose       |

---

# Why These Design Choices

## LangGraph

Used to build a controllable RAG workflow instead of a single monolithic chain.

This allows:

- query rewriting
- corrective retrieval
- groundedness checks
- retry routing
- conversation-aware orchestration

---

## Hybrid Retrieval (FAISS + BM25)

Vector search alone can miss:

- exact keywords
- IDs
- names
- short factual matches

BM25 improves lexical retrieval while FAISS improves semantic retrieval.

Combining both significantly improves recall quality.

---

## Corrective RAG

The system verifies whether retrieved context sufficiently supports the generated answer.

If confidence is low:

1. retrieval is retried
2. query is refined
3. unsupported answers are rejected

This reduces hallucination risk.

---

## Async Document Ingestion

Large documents should never block API requests.

Document processing runs asynchronously using:

- Celery
- Redis

The API immediately returns:

- document ID
- job status
- progress endpoint

---

## SentenceTransformers

Used instead of paid embedding APIs to:

- reduce cost
- simplify local development
- improve offline reproducibility

The model is cached during Docker build to improve startup speed.

---

# Retrieval Pipeline

## 1. Document Parsing

- PDF parsing using PyPDF
- DOCX parsing using python-docx

## 2. Chunking

- Sliding window chunking
- Overlapping chunks
- Metadata preservation

## 3. Embedding Generation

- SentenceTransformers embeddings
- Normalized vectors

## 4. Hybrid Retrieval

- FAISS semantic similarity
- BM25 keyword scoring
- Hybrid score fusion

## 5. Corrective RAG

- Context sufficiency evaluation
- Retry retrieval when needed

## 6. Answer Generation

- Groq LLM
- Strict grounded prompting

---

# Corrective RAG Flow

```text
User Question
      │
      ▼
Rewrite Query
      │
      ▼
Hybrid Retrieval
      │
      ▼
Generate Draft Answer
      │
      ▼
Groundedness Check
      │
 ┌────┴────┐
 │         │
Supported? No
 │         │
 ▼         ▼
Return   Retry Retrieval
Answer      │
            ▼
      Refined Retrieval
```

---

# Project Structure

```text
app/
├── api/
├── core/
├── db/
├── schemas/
├── services/
│   ├── ingestion/
│   └── qa/
├── tasks/
├── utils/
├── main.py
│
samples/
│
scripts/
│
docker-compose.yml
Dockerfile
README.md
.env.example
```

---

# Setup Instructions

## Prerequisites

- Docker Desktop
- Git

---

# 1. Clone Repository

```bash
git clone https://github.com/goswamishipra15/smart_doc_qa.git

cd smart_doc_qa
```

---

# 2. Configure Environment

Create `.env`

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/docqa

REDIS_URL=redis://redis:6379/0

GROQ_API_KEY=YOUR_GROQ_API_KEY

GROQ_MODEL=llama-3.3-70b-versatile

EMBEDDING_MODEL=sentence-transformers/paraphrase-MiniLM-L3-v2

UPLOAD_DIR=/app/data/uploads

FAISS_INDEX_PATH=/app/data/faiss_index

BM25_INDEX_PATH=/app/data/bm25

OMP_NUM_THREADS=1

TOKENIZERS_PARALLELISM=false
```

---

# 3. Run Entire Stack

```bash
docker compose up --build
```

---

# Services

| Service      | URL                        |
| ------------ | -------------------------- |
| FastAPI Docs | http://localhost:8000/docs |
| Flower       | http://localhost:5555      |

---

# API Workflow

## 1. Upload Document

### Endpoint

```http
POST /api/v1/documents
```

### Response

```json
{
  "document_id": "uuid",
  "status": "QUEUED"
}
```

---

## 2. Check Processing Status

### Endpoint

```http
GET /api/v1/documents/{document_id}/progress
```

### Response

```json
{
  "status": "READY",
  "progress": 100
}
```

---

## 3. Create Conversation

### Endpoint

```http
POST /api/v1/conversations
```

### Request

```json
{
  "document_id": "uuid",
  "title": "Policy Discussion"
}
```

---

## 4. Ask Question

### Endpoint

```http
POST /api/v1/ask
```

### Request

```json
{
  "document_id": "uuid",
  "conversation_id": "uuid",
  "question": "What is the leave policy?"
}
```

### Response

```json
{
  "answer": "Employees are eligible for paid leave after...",
  "conversation_id": "uuid",
  "document_id": "uuid",
  "answer_type": "grounded",
  "confidence": 0.92,
  "sources": [
    {
      "chunk_id": "uuid",
      "page_number": 4,
      "score": 0.88,
      "text": "..."
    }
  ]
}
```

---

# Failure Handling

## Unsupported File Types

Returns validation error.

---

## Corrupted PDFs

Gracefully fails ingestion and updates document status.

---

## LLM Failure

API returns stable error response without crashing ingestion.

---

## No Relevant Context

System returns:

```json
{
  "answer": "I could not find this information in the uploaded document."
}
```

instead of hallucinating.

---

## Async Status Tracking

Documents expose:

- processing state
- progress percentage
- failure details

---

# Performance Optimizations

## Embedding Model Caching

Embedding model is:

- downloaded during Docker build
- cached using HuggingFace cache volumes
- loaded once per process using singleton pattern

This significantly reduces startup time and memory usage.

---

## Apple Silicon Optimization

The worker uses:

- `--pool=solo`
- `--concurrency=1`

to avoid multiprocessing memory spikes on M1/M2 Macs.

---

# Future Improvements

- OCR support for scanned PDFs
- Streaming responses
- Reranking models
- Multi-document querying
- Authentication & RBAC
- S3/GCS storage integration
- Kubernetes deployment
- Observability & tracing

---

# Deployment

The system is fully containerized using Docker Compose.

Production deployment can be done using:

- AWS ECS
- Kubernetes
- Railway
- Render
- Fly.io

---

# Notes

This implementation intentionally focuses on:

- retrieval quality
- grounded generation
- modular architecture
- scalability
- async processing
- clean API design

rather than only building a minimal chatbot wrapper.

---

# Author

Shipra Goswami
