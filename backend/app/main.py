from fastapi import FastAPI
from .modules.owner.router import router as owner_router
from .modules.customers.router import customer_router
from .modules.dashboard.router import dashboardrouter
from .modules.item.router import item_router
from .modules.order.router import order_router
from .modules.shop.router import shop_router
from .modules.trader.router import trader_order_router
from .modules.transaction.router import transaction_router


app = FastAPI(title="gumasta.backend")
app.include_router(owner_router)
app.include_router(customer_router)
app.include_router(dashboardrouter)
app.include_router(item_router)
app.include_router(order_router)
app.include_router(shop_router)
app.include_router(trader_order_router)
app.include_router(transaction_router)


@app.get("/health")
def health_check():
    return {"message": "All Fine!"}