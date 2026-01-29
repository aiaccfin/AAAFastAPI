from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

engine = create_engine(settings.CFG['PG_AIACC'], echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def get_session_no_yield():
    # Open a new session
    session = Session(engine)
    return session  # Return the session object directly