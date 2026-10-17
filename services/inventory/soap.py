"""The same operation, the 2002 way: one URL, always POST, an XML envelope."""

import xml.etree.ElementTree as ET

from fastapi import APIRouter, Request, Response

from .data import PRODUCTS

router = APIRouter()

NS = {
    "env": "http://www.w3.org/2003/05/soap-envelope",
    "shop": "http://shop.example.com/",
}

ENVELOPE = """<?xml version="1.0"?>
<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
  <env:Body>
{body}
  </env:Body>
</env:Envelope>
"""

FOUND = """    <shop:GetProductResponse xmlns:shop="http://shop.example.com/">
      <shop:id>{id}</shop:id>
      <shop:name>{name}</shop:name>
      <shop:price_eur>{price_eur}</shop:price_eur>
      <shop:stock>{stock}</shop:stock>
    </shop:GetProductResponse>"""

FAULT = """    <env:Fault>
      <env:Code><env:Value>env:Sender</env:Value></env:Code>
      <env:Reason><env:Text xml:lang="en">No product {id}</env:Text></env:Reason>
    </env:Fault>"""


@router.post("/ProductService")
async def product_service(request: Request) -> Response:
    """One endpoint, one verb, and the operation hidden inside the body."""
    envelope = ET.fromstring(await request.body())
    asked_id = int(envelope.find(".//shop:id", NS).text)

    product = PRODUCTS.get(asked_id)
    body = FOUND.format(**product) if product else FAULT.format(id=asked_id)

    return Response(
        content=ENVELOPE.format(body=body),
        media_type="application/soap+xml",
    )
