from fastapi import APIRouter, Depends
from app.utils.u_auth_py import authent
from app.api.p1.product import product, category

product_router = APIRouter()

# Include all product-related routers
# IMPORTANT: Include category router FIRST so /category routes match before /{product_id}
product_router.include_router(category.router)
product_router.include_router(product.router)

