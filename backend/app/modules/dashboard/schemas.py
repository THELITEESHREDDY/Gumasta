from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class DashboardFilters(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    shop_id: str | None = None
    item_name: str | None = Field(default=None, min_length=1, max_length=150)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("start_date cannot be after end_date")
        return self


class SalesSummary(BaseModel):
    total_sales: Decimal
    total_orders: int
    average_order_value: Decimal


class DailySales(BaseModel):
    date: date
    sales: Decimal
    orders: int


class ItemSales(BaseModel):
    item_name: str
    quantity_sold: Decimal
    revenue: Decimal
    gross_profit: Decimal


class SalesDashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    filters: DashboardFilters
    summary: SalesSummary
    daily_sales: list[DailySales]
    top_items: list[ItemSales]


class ItemSales(BaseModel):
    item_id: str | None
    item_name: str
    quantity_sold: Decimal
    revenue: Decimal
    gross_profit: Decimal