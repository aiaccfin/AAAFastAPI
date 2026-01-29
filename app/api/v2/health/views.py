# views
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from sqlmodel import SQLModel

from app.db.conn import Session, get_session
from app.api.health.crud import get_health, get_stats
# print("--3-1-------------():", SQLModel.metadata.tables.keys())
from app.api.health.models import Health, Stats
from app.utils.logger import logger_config

router = APIRouter()
logger = logger_config(__name__)


@router.get(
    "",
    response_model=Health,
    status_code=status.HTTP_200_OK,
    responses={200: {"model": Health}},
)
def health(db: Session = Depends(get_session)):
    return get_health(db=db)


@router.get(
    "/stats",
    response_model=Stats,
    status_code=status.HTTP_200_OK,
    responses={200: {"model": Stats}},
)
def health_stats(db: Session = Depends(get_session)):
    return get_stats(db=db)
