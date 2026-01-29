# app/celery/celery_worker.py
from celery import Celery
import uuid, logging
# from app.repositories.repository_inv_vec import VectorRepository
from app.db.connection.conn_rls import get_super_session_factory
from app.models.rls.m_invoice_rls import InvoiceDB

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Celery instance
celery_app = Celery(
    "tasks",
    broker="redis://localhost:8080/0",
    backend="redis://localhost:8080/0",
)

TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"

@celery_app.task(bind=True)
def embed_invoice_task(self, invoice_id: str):
    logger.info(f"Celery task started for invoice {invoice_id}")

    session_factory = get_super_session_factory()
    session = next(session_factory())  # get a session generator

    invoice = session.get(InvoiceDB, uuid.UUID(invoice_id))
    if not invoice:
        logger.error(f"Invoice {invoice_id} not found")
        return

    logger.info(f"Invoice {invoice_id} retrieved from DB")

    # Save vector / fallback content via repository
    # vector_repo = VectorRepository()
    # vec_entry = vector_repo.save_invoice_vector(invoice=invoice, session=session)

    # logger.info(f"Celery task finished for invoice {invoice_id}, vector_id={vec_entry.id}")
