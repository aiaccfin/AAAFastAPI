from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from app.config import Settings
from app.utils.logger import logger_config

# from app.middlewares.request_context import RequestContextMiddleware

from app.api import rou

from app.db.connection import conn_rls, seed_data_gst, seed_invoices

logger = logger_config(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn_rls.create_db_and_tables()
    seed_data_gst.create_seeds()
    # seed_invoices.create_invoice_seeds()
    yield


def create_app(settings: Settings):
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/",
        description=settings.DESCRIPTION,
        lifespan=lifespan,
    )

    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,

        allow_origins=["*"],
        allow_credentials=False,  # MUST be False when origins="*"

        allow_methods=["*"],
        allow_headers=["*"],
    )

    # app.add_middleware(RequestContextMiddleware)
    app.include_router(rou)

    return app
