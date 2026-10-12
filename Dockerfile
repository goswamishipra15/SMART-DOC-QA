# FROM python:3.11-slim

# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1
# ENV PIP_NO_CACHE_DIR=1

# # Important for transformers stability
# ENV TOKENIZERS_PARALLELISM=false
# ENV OMP_NUM_THREADS=1

# WORKDIR /app

# # System dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     gcc \
#     curl \
#     git \
#     && rm -rf /var/lib/apt/lists/*

# # Install Python dependencies first for better Docker layer caching
# COPY requirements.txt ./

# RUN pip install --upgrade pip && \
#     pip install -r requirements.txt

# # Pre-download embedding model during build
# # This avoids downloading at runtime
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L3-v2')"

# # Copy application
# COPY . .

# # Make scripts executable
# RUN chmod +x scripts/entrypoint.sh

# # Create runtime directories
# RUN mkdir -p /app/data/uploads && \
#     mkdir -p /app/data/faiss_index && \
#     mkdir -p /app/data/bm25

# EXPOSE 8000




FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Transformers / tokenizer stability
ENV TOKENIZERS_PARALLELISM=false
ENV OMP_NUM_THREADS=1

# HuggingFace offline/cache settings
ENV HF_HOME=/root/.cache/huggingface
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/root/.cache/huggingface

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Pre-download embedding model during build
# VERY IMPORTANT
RUN python - <<EOF
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "sentence-transformers/paraphrase-MiniLM-L3-v2"
)

print("Embedding model cached successfully")
EOF

# Copy project
COPY . .

# Make scripts executable
RUN chmod +x scripts/entrypoint.sh

# Runtime directories
RUN mkdir -p /app/data/uploads && \
    mkdir -p /app/data/faiss_index && \
    mkdir -p /app/data/bm25

EXPOSE 8000