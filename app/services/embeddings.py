"""Encodeur bge-m3 (1024 dims), chargé une seule fois par processus."""
from __future__ import annotations

import numpy as np

from ..config import settings

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed(texts: list[str]) -> list[list[float]]:
    """Textes -> vecteurs denses normalisés (dimension settings.embedding_dim)."""
    model = _get_model()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return np.asarray(vectors, dtype=np.float32).tolist()


def embed_query(text: str) -> list[float]:
    return embed([text])[0]
