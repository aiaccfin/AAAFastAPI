# app/services/service_salestax.py
from app.repositories.repository_salestax import GST26Repository
from app.schemas.schema_salestax import GST26Create
from fastapi import HTTPException

class GST26Service:
    def __init__(self, repository: GST26Repository):
        self.repository = repository

    async def create_entry(self, entry: GST26Create) -> dict:
        # calculate net_tax_due
        total_taxes = sum(entry.taxes_collected.dict().values())
        total_adjustments = sum(entry.adjustments.dict().values())
        entry.net_tax_due = total_taxes - total_adjustments

        try:
            return await self.repository.create_entry(entry)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))



    async def fetch_all_entries(self) -> list[dict]:
        try:
            return await self.repository.fetch_all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    async def update_entry(self, entry_id: str, update_data: dict) -> dict:
        # Recalculate net_tax_due if taxes_collected or adjustments are being updated
        if "taxes_collected" in update_data or "adjustments" in update_data:
            current_data = await self.repository.fetch_all()  # or fetch by ID if you implement fetch_by_id
            current_entry = next((e for e in current_data if e["_id"] == entry_id), None)
            if not current_entry:
                raise HTTPException(status_code=404, detail=f"Entry {entry_id} not found")

            # Merge current with update for calculation
            taxes = current_entry.get("taxes_collected", {})
            adjustments = current_entry.get("adjustments", {})

            if "taxes_collected" in update_data:
                taxes.update(update_data["taxes_collected"])
            if "adjustments" in update_data:
                adjustments.update(update_data["adjustments"])

            update_data["net_tax_due"] = sum(taxes.values()) - sum(adjustments.values())

        try:
            return await self.repository.update_entry(entry_id, update_data)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))