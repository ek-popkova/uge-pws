"""The contract of the Orders service."""

from pydantic import BaseModel, Field


class OrderIn(BaseModel):
    """What a client sends to place an order."""

    product_id: int = Field(examples=[42])
    quantity: int = Field(gt=0, le=10, examples=[2])


class Order(BaseModel):
    """An order, as the service stores it."""

    id: int
    product_id: int
    quantity: int
    total_eur: float


class Error(BaseModel):
    detail: str
