# app/api/v7/endpoint_salestax.py
from fastapi import APIRouter, Depends, Body
from app.schemas.schema_salestax import GST26Create
from app.services.service_salestax import GST26Service
from app.repositories.repository_salestax import GST26Repository
from app.db.x_mg_conn import salestax_collection

router = APIRouter()

def get_service() -> GST26Service:
    repository = GST26Repository(salestax_collection)
    return GST26Service(repository)

@router.post("/", response_model=dict, summary="Create a new GST26 entry.")
async def create_entry(entry: GST26Create, service: GST26Service = Depends(get_service)):
    return await service.create_entry(entry)



@router.get("/", response_model=list[dict], summary="Fetch all GST26 entries.")
async def get_all_entries(service: GST26Service = Depends(get_service)):
    return await service.fetch_all_entries()


@router.put("/{entry_id}", response_model=dict, summary="Update an existing GST26 entry.")
async def update_entry(
    entry_id: str,
    update_data: dict = Body(...),
    service: GST26Service = Depends(get_service)
):
    """
    Update an existing GST26 entry by its internal _id.
    """
    return await service.update_entry(entry_id, update_data)
