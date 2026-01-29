from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.connection.conn_rls import tenant_session_dependency
from app.models.rls.m_gst_rls import GSTTable, GSTCreate, GSTRead, GSTUpdateRequest
from app.services.service_gst62 import gst62_service

router = APIRouter()
TENANT_ID = "550e8400-e29b-41d4-a716-446655440000"
ROLE_ID = "112"
USER_ID = "111"

get_session = tenant_session_dependency(TENANT_ID)


@router.get("/", response_model=list[GSTRead])
async def list_tax_rates(session: Session = Depends(tenant_session_dependency(TENANT_ID))):
    return gst62_service.list_gst(session)


@router.post("/", response_model=GSTRead)
async def create_tax_rate(    data: GSTCreate,    session: Session = Depends(tenant_session_dependency(TENANT_ID))):
   
    # Make SQLModel instance
    new_gst = GSTTable(**data.dict(), tenant_id=TENANT_ID)

    session.add(new_gst)
    session.commit()
    session.refresh(new_gst)

    return new_gst



@router.get("/code/{gst_code}", response_model=GSTRead)
async def get_tax_rate_by_code(gst_code: str,    session: Session = Depends(get_session),
):
    statement = select(GSTTable).where(GSTTable.tax_code == gst_code)
    result = session.exec(statement).first()

    if not result:
        raise HTTPException(status_code=404, detail="GST not found")

    return result




@router.put("", response_model=GSTRead)
async def update_tax_rate(
    data: GSTUpdateRequest,
    session: Session = Depends(get_session),
):
    # 1️⃣ Fetch existing record
    gst_record = session.exec(select(GSTTable).where(GSTTable.tax_code == data.tax_code)).first()

    # 2️⃣ Fail if not found
    if not gst_record:
        raise HTTPException(status_code=404, detail="GST not found")

    # 3️⃣ Ensure the field exists on the table
    if not hasattr(GSTTable, data.field_name):
        raise HTTPException(status_code=400, detail=f"Field {data.field_name} does not exist")

    # 4️⃣ Update the existing record
    setattr(gst_record, data.field_name, data.new_value)

    # 5️⃣ Commit and refresh
    session.commit()
    session.refresh(gst_record)

    return gst_record