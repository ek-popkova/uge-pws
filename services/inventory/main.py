"""Inventory service: what is in stock."""

from fastapi import FastAPI, HTTPException

from .data import PRODUCTS
from .soap import router as soap_router

app = FastAPI(title="Inventory service", version="0.1.0")
app.include_router(soap_router)


@app.get("/products")
def list_products():
    """Every product the shop knows about."""
    return list(PRODUCTS.values())


@app.get("/products/{product_id}")
def get_product(product_id: int):
    """One product, by id."""
    product = PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail=f"No product {product_id}")
    return product


CART: list[int] = []          # a cart the service keeps in its own memory


@app.post("/cart/{product_id}")
def add_to_cart(product_id: int):
    """Put a product in the cart, and keep it in this process."""
    CART.append(product_id)
    return {"cart": CART, "served_by": id(CART)}
