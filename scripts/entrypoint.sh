#!/usr/bin/env bash
set -euo pipefail
MODE="${1:-api}"
mkdir -p /data/uploads /data/faiss_index /data/bm25
if [ "$MODE" = "api" ]; then
  alembic upgrade head
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
elif [ "$MODE" = "worker" ]; then
  exec celery -A app.tasks.celery_app.celery_app worker --loglevel=INFO --concurrency=1
elif [ "$MODE" = "flower" ]; then
  exec celery -A app.tasks.celery_app.celery_app flower --port=5555
else
  echo "Unknown mode: $MODE"
  exit 1
fi
