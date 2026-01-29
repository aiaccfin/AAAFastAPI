# tests/test_documents_query.py
import pytest
from fastapi.testclient import TestClient
from app.main_rls import create_app
from app.config import Settings4Test
from app.api.rag import rag_query

@pytest.fixture
def client():
    app = create_app(Settings4Test())
    return TestClient(app)

def smoke_test_query_rag(client, monkeypatch):
    # Mock EmbeddingService.embed
    async def fake_embed(self, texts):
        return [[0.1, 0.2, 0.3]]

    monkeypatch.setattr(rag_query.EmbeddingService, "embed", fake_embed)

    # Mock RetrievalService.search
    def fake_search(self, query_embedding, top_k):
        return [{
            "chunk_id": "c1",
            "document_id": "d1",
            "content": "hello world",
            "similarity": 0.99
        }]

    monkeypatch.setattr(rag_query.RetrievalService, "search", fake_search)

    response = client.post("/rag/query", json={"query": "hello", "top_k": 1})

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["chunk_id"] == "c1"
