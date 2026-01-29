import os
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.LoggedCollection import LoggedCollection

MONGO_URI = os.getenv("MONGO_AIACCFIN")
client = AsyncIOMotorClient(MONGO_URI)
db = client.db_xai

# Define log collection first (no wrapper)
crud_logs_collection = db.crud_logs

# Now wrap the rest
users_collection  = LoggedCollection(db.users, "users", crud_logs_collection)
roles_collection  = LoggedCollection(db.roles, "roles", crud_logs_collection)
groups_collection = LoggedCollection(db.groups, "groups", crud_logs_collection)
invoice_collection = LoggedCollection(db.invoices, "invoices", crud_logs_collection)
workers_collection = LoggedCollection(db.workers, "workers", crud_logs_collection)
dynamic_collection = LoggedCollection(db.dynamic_workers, "dynamic_workers", crud_logs_collection)
biz_entities_collection = LoggedCollection(db.biz_entities, "biz_entities", crud_logs_collection)
verification_collection = LoggedCollection(db.verification_collection, "verification", crud_logs_collection)
transaction_collection = LoggedCollection(db.transactions, "transactions", crud_logs_collection)
item_collection = LoggedCollection(db.items, "items", crud_logs_collection)
product_collection = LoggedCollection(db.products, "products", crud_logs_collection)
vendor_collection = LoggedCollection(db.vendors, "vendors", crud_logs_collection)
customer_collection = LoggedCollection(db.customers, "customers", crud_logs_collection)
receipt_collection = LoggedCollection(db.receipts, "receipts", crud_logs_collection)
coa_collection = LoggedCollection(db.coa, "coa", crud_logs_collection)
bs_collection = LoggedCollection(db.bankstatements, "bankstatements", crud_logs_collection)
salestax_collection = LoggedCollection(db.salestax, "salestax", crud_logs_collection)



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
crud_logs_collection = db.xai_db_log