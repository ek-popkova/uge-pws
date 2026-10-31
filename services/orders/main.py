"""Orders service: places an order by asking Inventory, over HTTP, like any other client."""

import os

import httpx
from fastapi import FastAPI, HTTPException, Response, status

from . import db
from .models import Error, Order, OrderIn

INVENTORY_URL = os.environ.get("INVENTORY_URL", "http://127.0.0.1:8000")

app = FastAPI(title="Orders service", version="0.1.0")
db.init()


@app.post(
    "/orders",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": Error, "description": "Not enough stock"},
        422: {"model": Error, "description": "Unknown product, or invalid order"},
        502: {"model": Error, "description": "Inventory answered something unexpected"},
        503: {"model": Error, "description": "Inventory cannot be reached"},
    },
    tags=["orders"],
)
def place_order(order: OrderIn, response: Response):
    """Check the product, reserve the units, then record the order."""
    try:
        product = httpx.get(f"{INVENTORY_URL}/products/{order.product_id}", timeout=2)
        if product.status_code == 404:
            raise HTTPException(status_code=422, detail=f"No product {order.product_id}")
        reservation = httpx.post(
            f"{INVENTORY_URL}/products/{order.product_id}/reservations",
            json={"quantity": order.quantity},
            timeout=2,
        )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Inventory cannot be reached")

    if reservation.status_code == 409:
        raise HTTPException(status_code=409, detail=reservation.json()["detail"])
    if product.status_code != 200 or reservation.status_code != 201:
        raise HTTPException(status_code=502, detail="Unexpected answer from Inventory")

    total = round(product.json()["price_eur"] * order.quantity, 2)
    order_id = db.create_order(order.product_id, order.quantity, total)
    response.headers["Location"] = f"/orders/{order_id}"
    return db.get_order(order_id)


@app.get("/orders/{order_id}", response_model=Order, responses={404: {"model": Error}}, tags=["orders"])
def get_order(order_id: int):
    order = db.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"No order {order_id}")
    return order


@app.get("/orders", response_model=list[Order], tags=["orders"])
def list_orders():
    return db.list_orders()
