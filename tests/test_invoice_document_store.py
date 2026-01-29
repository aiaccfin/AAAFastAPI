# tests/test_invoice_document_store.py
import pytest
from dotenv import load_dotenv
from haystack import Document
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack_integrations.components.retrievers.pgvector import PgvectorKeywordRetriever
from datetime import datetime
import uuid

load_dotenv()  # loads PG_CONN_STR from .env

def test_pgvector_document_store_write_and_read():
    """
    Test Step 1: Verify PgvectorDocumentStore can create table, insert, and retrieve documents.
    """

    # Initialize document store
    document_store = PgvectorDocumentStore(
        embedding_dimension=1536,
        table_name="invoice_embeddings",
        recreate_table=False,  # correct argument to recreate table
    )

    # Make sure the store is empty
    document_store.delete_all_documents()

    # Sample invoice document
    sample_doc = Document(
        content="Invoice #INV-TEST Test invoice insertion",
        tenant_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

    )

    # Write the document
    document_store.write_documents([sample_doc])

    # Retrieve documents with keyword retriever
    retriever = PgvectorKeywordRetriever(document_store=document_store, top_k=5)
    results = retriever.run(query="INV-TEST")

    docs = results["documents"]

    # Validate
    assert len(docs) >= 1
    assert "Invoice #INV-TEST" in docs[0].content
