import os, time, contextvars
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_AIACCFIN")

client = AsyncIOMotorClient(MONGO_URI)
db = client.db_xai

# Request context变量
request_context = contextvars.ContextVar("request_context", default={})

class LoggingCollection:
    def __init__(self, collection):
        self.collection = collection

    async def log_crud(self, operation, filter_doc=None, data=None):
        ctx = request_context.get()
        await db.xai_db_log.insert_one({
            "request_id": ctx.get("request_id"),
            "user": ctx.get("user"),
            "client_ip": ctx.get("client_ip"),
            "operation": operation,
            "collection": self.collection.name,
            "filter": filter_doc,
            "data": data,
            "timestamp": time.time()
        })

    async def insert_one(self, document):
        result = await self.collection.insert_one(document)
        await self.log_crud("insert", data=document)
        return result

    async def find_one_and_update(self, filter_doc, update_doc, **kwargs):
        result = await self.collection.find_one_and_update(filter_doc, update_doc, **kwargs)
        await self.log_crud("update", filter_doc=filter_doc, data=update_doc)
        return result

    async def find_one(self, filter_doc):
        result = await self.collection.find_one(filter_doc)
        await self.log_crud("find", filter_doc=filter_doc)
        return result

    async def delete_one(self, filter_doc):
        result = await self.collection.delete_one(filter_doc)
        await self.log_crud("delete", filter_doc=filter_doc)
        return result

# 把现有collection封装成LoggingCollection
users_collection  = LoggingCollection(db.users)
roles_collection  = LoggingCollection(db.roles)
groups_collection = LoggingCollection(db.groups)
invoice_collection = LoggingCollection(db.invoices)
workers_collection = LoggingCollection(db.workers)
dynamic_collection = LoggingCollection(db.dynamic_workers)
biz_entities_collection = LoggingCollection(db.biz_entities)
verification_collection = LoggingCollection(db.verification_collection)
transaction_collection = LoggingCollection(db.transactions)
item_collection = LoggingCollection(db.items)
product_collection = LoggingCollection(db.products)
vendor_collection = LoggingCollection(db.vendors)
customer_collection = LoggingCollection(db.customers)
receipt_collection = LoggingCollection(db.receipts)
coa_collection = LoggingCollection(db.coa)
bs_collection = LoggingCollection(db.bankstatements)



# import os
# from motor.motor_asyncio import AsyncIOMotorClient

# MONGO_URI= os.getenv("MONGO_AIACCFIN")

# client = AsyncIOMotorClient(MONGO_URI)
# db     = client.db_xai

# users_collection  =  db.users
# roles_collection  =  db.roles
# groups_collection =  db.groups
# invoice_collection =  db.invoices
# workers_collection = db.workers
# dynamic_collection = db.dynamic_workers

# biz_entities_collection = db.biz_entities
# verification_collection = db.verification_collection

# transaction_collection = db.transactions
# item_collection = db.items
# product_collection = db.products
# vendor_collection = db.vendors
# customer_collection = db.customers
# receipt_collection = db.receipts

# coa_collection = db.coa

# bs_collection = db.bankstatements