from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Query
from app.schemas.s_invoice import InvoiceModel
from app.services.service_inv import InvoiceService

router = APIRouter()

EXAMPLE_FILTER = {
    "client_name": "Alice",
    "status": {"$in": ["paid", "pending"]},
    "total": {"$gte": 100, "$lte": 1000},
    "created_at": {"$gte": "2025-01-01T00:00:00", "$lte": "2025-12-31T23:59:59"},
    "description": {"$regex": ".*subscription.*", "$options": "i"},
}


@router.post(
    "/universal_filter_paginated",
    response_model=List[InvoiceModel],
    summary="Filter invoices with multiple conditions and return paginated results.",
    description="Filter invoices using a flexible JSON object with pagination and sorting.",
)
async def universal_filter(
    filters: Dict[str, Any] = Body(..., example=EXAMPLE_FILTER),
    sort_by: Optional[str] = Query(
        "created_at", description="Field to sort by"),
    sort_dir: Optional[int] = Query(-1,
                                    description="Sort direction: 1=asc, -1=desc"),
    skip: Optional[int] = Query(
        0, ge=0, description="Number of documents to skip"),
    limit: Optional[int] = Query(
        50, ge=1, le=100, description="Max number of documents to return"
    ),
):
    """
    Fully dynamic invoice filtering.
    Frontend can send any combination of fields and MongoDB operators.
    Supports sorting, skipping, and limiting for pagination.
    """
    return await InvoiceService.universal_filter_invoices_paginated(
        filters=filters, sort_by=sort_by, sort_dir=sort_dir, skip=skip, limit=limit
    )


@router.post(
    "/universal_filter",
    response_model=List[InvoiceModel],
    summary="Filter invoices using multiple criteria without pagination.",
    description="Filter invoices using a flexible JSON object.",
)
async def universal_filter(filters: Dict[str, Any] = Body(..., example=EXAMPLE_FILTER)):
    """
    Accepts any JSON object as filters.
    Example request body:
    {
        "client_name": "Alice",
        "status": "paid",
        "total": {"$gte": 100, "$lte": 1000},
        "created_at": {"$gte": "2025-01-01T00:00:00"}
    }
    """
    return await InvoiceService.universal_filter_invoices(filters)


@router.get(
    "/filter",
    response_model=List[InvoiceModel],
    description="Filter invoices using specific query parameters.",
    summary="Filter invoices with specific query parameters.",
)
async def filter_invoices(
    client_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    min_total: Optional[float] = Query(None),
    max_total: Optional[float] = Query(None),
):
    filters: Dict[str, Any] = {}
    if client_name:
        filters["client_name"] = client_name
    if status:
        filters["status"] = status
    if min_total is not None or max_total is not None:
        filters["total"] = {}
        if min_total is not None:
            filters["total"]["$gte"] = min_total
        if max_total is not None:
            filters["total"]["$lte"] = max_total

    return await InvoiceService.filter_invoices(filters)


@router.post("/",    response_model=InvoiceModel,    description="Create a new invoice.",    summary="Create a new invoice.",)
async def create_invoice(invoice: InvoiceModel):
    return await InvoiceService.create_invoice(invoice)


@router.put(
    "/{inv_id}",
    response_model=InvoiceModel,
    description="Update an existing invoice using its invoice number.",
    summary="Update an existing invoice.",
)
async def update_invoice(inv_id: str, update_data: Dict[str, Any]):
    return await InvoiceService.update_invoice(inv_id, update_data)


@router.get(
    "/{invoice_number}",
    response_model=InvoiceModel,
    description="Retrieve a specific invoice by its invoice number.",
    summary="Retrieve a specific invoice.",
)
async def get_invoice(invoice_number: int):
    return await InvoiceService.get_invoice(invoice_number)


@router.get(
    "/",
    response_model=List[InvoiceModel],
    description="Retrieve a list of all invoices.",
    summary="Retrieve a list of all invoices.",
)
async def list_invoices():
    return await InvoiceService.list_invoices()


@router.post("/invoices/{inv_id}/duplicate", response_model=Dict[str, Any])
async def duplicate_invoice(inv_id: str):
    duplicated = await InvoiceService.duplicate_invoice(inv_id)
    return duplicated
