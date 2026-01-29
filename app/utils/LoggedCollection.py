from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection

class LoggedCollection:
    def __init__(self, collection, name, log_collection):
        self.collection = collection
        self.name = name
        self.log_collection = log_collection

    def __getattr__(self, name):
        # Anything we didn’t override just goes to the real Motor collection
        return getattr(self.collection, name)

    async def insert_one(self, document, performed_by=None):
        result = await self.collection.insert_one(document)
        # remove ObjectId from data before logging
        doc_copy = {**document}
        doc_copy.pop("_id", None)
        await self._log("CREATE", result.inserted_id, doc_copy, performed_by)
        return result

    async def find_one(self, filter, *args, performed_by=None, **kwargs):
        doc = await self.collection.find_one(filter, *args, **kwargs)
        doc_copy = {**doc} if doc else None
        if doc_copy:
            doc_copy.pop("_id", None)
        await self._log("READ_ONE", document_id=filter, data=doc_copy, performed_by=performed_by)
        return doc

    async def update_one(self, filter, update, *args, performed_by=None, **kwargs):
        result = await self.collection.update_one(filter, update, *args, **kwargs)
        await self._log("UPDATE", document_id=filter, data=update, performed_by=performed_by)
        return result

    async def delete_one(self, filter, *args, performed_by=None, **kwargs):
        result = await self.collection.delete_one(filter, *args, **kwargs)
        await self._log("DELETE", document_id=filter, performed_by=performed_by)
        return result

    async def _log(self, operation, document_id=None, data=None, performed_by=None):
        from datetime import datetime
        entry = {
            "operation": operation,
            "collection": self.name,
            "user_id":"Jack",
            "document_id": str(document_id) if document_id else None,
            "data": data,
            "performed_by": performed_by,
            "timestamp": datetime.utcnow(),
        }
        await self.log_collection.insert_one(entry)
