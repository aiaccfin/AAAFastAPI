# app/conn_rls.py
from sqlmodel import Session, SQLModel, create_engine, text
from app.config import settings
from typing import Generator

engine = create_engine(settings.CFG["PG_POSTGRES"], echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session_user_id(user_id: int):
    session = Session(engine)
    # 👇 this line sets PostgreSQL session variable for RLS
    session.exec(f"SET app.current_user_id = {user_id}")
    return session

def get_session() -> Generator[Session, None, None]:
    """用于 FastAPI 依赖注入的会话（无租户上下文）"""
    with Session(engine) as session:
        yield session


def get_session_no_yield():
    """直接返回会话对象（无租户上下文）"""
    return Session(engine)


# 🔥 新增：获取租户感知的会话
def get_tenant_session(tenant_id: str) -> Generator[Session, None, None]:
    """获取设置了 RLS 上下文的数据库会话"""
    with Session(engine) as session:
        # 关键：设置当前租户上下文
        session.exec(text(f"SET app.current_tenant = '{tenant_id}'"))
        try:
            yield session
        finally:
            # 清理上下文（可选）
            session.exec(text("RESET app.current_tenant"))


def get_tenant_session_no_yield(tenant_id: str) -> Session:
    """直接返回设置了租户上下文的会话对象"""
    session = Session(engine)
    session.exec(text(f"SET app.current_tenant = '{tenant_id}'"))
    return session
