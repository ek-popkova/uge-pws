"""Inventory service: the stock, behind a uniform interface."""

from fastapi import FastAPI, HTTPException, Query, Response, status

from . import db
from .models import Error, Product, ProductIn, ProductPatch, Reservation, ReservationIn
from .soap import router as soap_router

app = FastAPI(title="Inventory service", version="0.2.0")
app.include_router(soap_router)
db.init()

NOT_FOUND = {404: {"model": Error, "description": "No such product"}}


def not_found(product_id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"No product {product_id}")


@app.get("/products", response_model=list[Product], tags=["products"])
def list_products(
    in_stock: bool | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """The catalogue, one page at a time, optionally only what is in stock."""
    return db.list_products(in_stock, limit, offset)


@app.get("/products/{product_id}", response_model=Product, responses=NOT_FOUND, tags=["products"])
def get_product(product_id: int):
    """One product, by id."""
    product = db.get_product(product_id)
    if product is None:
        raise not_found(product_id)
    return product


@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED, tags=["products"])
def create_product(product: ProductIn, response: Response):
    """Add a product. The service chooses the id and says where to find it."""
    product_id = db.create_product(product.model_dump())
    response.headers["Location"] = f"/products/{product_id}"
    return db.get_product(product_id)


@app.put("/products/{product_id}", response_model=Product, responses=NOT_FOUND, tags=["products"])
def replace_product(product_id: int, product: ProductIn):
    """Replace a product entirely. Sending it twice changes nothing more."""
    if not db.update_product(product_id, product.model_dump()):
        raise not_found(product_id)
    return db.get_product(product_id)


@app.patch("/products/{product_id}", response_model=Product, responses=NOT_FOUND, tags=["products"])
def update_product(product_id: int, patch: ProductPatch):
    """Change only the fields that are sent."""
    if not db.update_product(product_id, patch.model_dump(exclude_unset=True, exclude_none=True)):
        raise not_found(product_id)
    return db.get_product(product_id)


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND, tags=["products"])
def delete_product(product_id: int):
    """Remove a product. Nothing to send back."""
    if not db.delete_product(product_id):
        raise not_found(product_id)


@app.post(
    "/products/{product_id}/reservations",
    response_model=Reservation,
    status_code=status.HTTP_201_CREATED,
    responses={**NOT_FOUND, 409: {"model": Error, "description": "Not enough stock"}},
    tags=["reservations"],
)
def reserve(product_id: int, reservation: ReservationIn):
    """Set units aside for an order: the action 'reserve' modelled as a new resource."""
    if db.get_product(product_id) is None:
        raise not_found(product_id)
    if not db.reserve(product_id, reservation.quantity):
        raise HTTPException(status_code=409, detail=f"Not enough stock for product {product_id}")
    return {
        "product_id": product_id,
        "quantity": reservation.quantity,
        "stock_left": db.get_product(product_id)["stock"],
    }
