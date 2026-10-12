# from __future__ import annotations
# from functools import lru_cache
# from sentence_transformers import SentenceTransformer
# from app.core.config import get_settings
# settings = get_settings()
# @lru_cache(maxsize=1)
# def get_embedding_model() -> SentenceTransformer: return SentenceTransformer(settings.embedding_model)
# def embed_texts(texts: list[str]) -> list[list[float]]:
#     model = get_embedding_model()
#     vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
#     return vectors.tolist()

# from __future__ import annotations

# import os
# from functools import lru_cache

# from sentence_transformers import SentenceTransformer

# from app.core.config import get_settings

# settings = get_settings()

# # Important for Apple Silicon / Docker stability
# os.environ["TOKENIZERS_PARALLELISM"] = "false"
# os.environ["OMP_NUM_THREADS"] = "1"


# @lru_cache(maxsize=1)
# def get_embedding_model() -> SentenceTransformer:
#     """
#     Load embedding model only once per process.
#     Uses CPU explicitly for Docker + Apple Silicon stability.
#     """

#     print(f"Loading embedding model: {settings.embedding_model}")

#     model = SentenceTransformer(
#         settings.embedding_model,
#         device="cpu",
#     )

#     return model


# def embed_texts(texts: list[str]) -> list[list[float]]:
#     """
#     Generate normalized embeddings.
#     """

#     if not texts:
#         return []

#     model = get_embedding_model()

#     vectors = model.encode(
#         texts,
#         normalize_embeddings=True,
#         show_progress_bar=False,
#         batch_size=8,
#         convert_to_numpy=True,
#     )

#     return vectors.tolist()


from __future__ import annotations

import os
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

settings = get_settings()

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    print(
        f"Loading embedding model: "
        f"{settings.embedding_model}"
    )

    model = SentenceTransformer(
        settings.embedding_model,
        device="cpu",
        local_files_only=True,
    )

    return model


def embed_texts(
    texts: list[str],
) -> list[list[float]]:
    if not texts:
        return []

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=8,
        convert_to_numpy=True,
    )

    return vectors.tolist()