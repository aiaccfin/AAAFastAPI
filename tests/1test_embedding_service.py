# tests/test_embedding_service.py
import asyncio
from app.services.rag.embeddings import EmbeddingService


def test_embed_returns_list_of_lists():
    service = EmbeddingService()
    texts = ["hello", "world"]

    embeddings = asyncio.run(service.embed(texts))

    assert isinstance(embeddings, list)
    assert len(embeddings) == len(texts)

    for emb in embeddings:
        assert isinstance(emb, list)
