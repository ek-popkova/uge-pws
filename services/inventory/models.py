"""The contract of the Inventory service: what goes in, what comes out."""

from pydantic import BaseModel, Field


class ProductIn(BaseModel):
    """What a client sends to create or replace a product."""

    name: str = Field(min_length=1, max_length=80, examples=["Espresso machine"])
    price_eur: float = Field(gt=0, examples=[189.90])
    stock: int = Field(ge=0, examples=[7])


class ProductPatch(BaseModel):
    """A partial update: send only the fields that change."""

    name: str | None = Field(default=None, min_length=1, max_length=80)
    price_eur: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)


class Product(BaseModel):
    """What the service sends back: the fields, and the id it chose."""

    id: int
    name: str
    price_eur: float
    stock: int


class ReservationIn(BaseModel):
    """A request to set some units aside for an order."""

    quantity: int = Field(gt=0, examples=[2])


class Reservation(BaseModel):
    """A reservation that succeeded."""

    product_id: int
    quantity: int
    stock_left: int


class Error(BaseModel):
    """The shape of every error this service returns."""

    detail: str
