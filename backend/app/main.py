from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from  app.db.session import get_db
from app.routers.auth import router as auth_router
from app.routers.shop import router as shop_router
from app.routers.product import router as product_router
from app.routers.customer import router as customer_router
from app.routers.order import router as order_router


app = FastAPI(
    title="Gumasta API",
    version="0.1.0"
)
app.include_router(product_router)
app.include_router(customer_router)
app.include_router(auth_router)
app.include_router(shop_router)
app.include_router(order_router)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/health/db")
async def database_health(
    db: AsyncSession = Depends(get_db)
):
    await db.execute(text("SELECT 1"))

    return {"database": "connected"}