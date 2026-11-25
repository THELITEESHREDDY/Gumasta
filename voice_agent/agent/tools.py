import re

from services.gumasta_api import GumastaAPI
from decimal import Decimal

async def find_customer(
    api: GumastaAPI,
    shop_id: str,
    mobile: str
):
    customers = await api.get_customers(
        shop_id,
        search=mobile
    )

    for customer in customers:
        if customer["mobile"] == mobile:
            return customer

    return None


async def get_or_create_customer(
    api: GumastaAPI,
    shop_id: str,
    mobile: str,
    name: str | None = None
):
    mobile = mobile.strip()

    if not re.fullmatch(r"\+?[0-9]{10}", mobile):
        raise ValueError("Invalid mobile number")

    customer = await find_customer(
        api,
        shop_id,
        mobile
    )

    if customer:
        return {
            "status": "existing",
            "customer": customer
        }

    if not name or not name.strip():
        return {
            "status": "name_required",
            "customer": None
        }

    customer = await api.create_customer(
        shop_id,
        name=name.strip(),
        mobile=mobile
    )

    return {
        "status": "created",
        "customer": customer
    }

async def find_product(
    api: GumastaAPI,
    shop_id: str,
    product_name: str
):
    products = await api.get_products(shop_id)

    product_name = product_name.strip().casefold()

    for product in products:
        if product["name"].strip().casefold() == product_name:
            return product

    return None


async def get_product_catalogue(
    api: GumastaAPI,
    shop_id: str
):
    products = await api.get_products(shop_id)

    return [
        {
            "product_id": product["id"],
            "name": product["name"],
            "selling_price": product["selling_price"],
            "unit": product["unit"]
        }
        for product in products
    ]

async def calculate_order_total(
    api: GumastaAPI,
    shop_id: str,
    items: list[dict]
):
    if not items:
        raise ValueError("Order cannot be empty")

    catalogue = await get_product_catalogue(
        api, shop_id
    )

    products = {
        product["product_id"]: product
        for product in catalogue
    }

    quantities = {}

    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        if type(quantity) is not int or quantity <= 0:
            raise ValueError("Invalid quantity")

        if product_id not in products:
            raise ValueError("Product not found")

        quantities[product_id] = (
            quantities.get(product_id, 0) + quantity
        )

    order_items = []
    total_amount = Decimal("0.00")

    for product_id, quantity in quantities.items():

        product = products[product_id]

        unit_price = Decimal(product["selling_price"])
        subtotal = unit_price * quantity

        order_items.append({
            "product_id": product_id,
            "product_name": product["name"],
            "quantity": quantity,
            "unit": product["unit"],
            "unit_price": str(unit_price),
            "subtotal": str(subtotal)
        })

        total_amount += subtotal

    return {
        "order_items": order_items,
        "total_amount": str(total_amount)
    }


async def place_order(
    api: GumastaAPI,
    shop_id: str,
    customer_id: str,
    order_items: list[dict],
    confirmed: bool
):
    if confirmed is not True:
        raise ValueError("Customer confirmation required")

    if not order_items:
        raise ValueError("Order cannot be empty")

    payload = [
        {
            "product_id": item["product_id"],
            "quantity": item["quantity"],
            "unit_price": item["unit_price"]
        }
        for item in order_items
    ]

    return await api.create_order(
        shop_id=shop_id,
        customer_id=customer_id,
        order_items=payload
    )