"""A client of the shop's MCP server: it does the job of the assistant app, without the model."""

import anyio
from mcp import Client
from mcp.types import ElicitResult


async def ask_the_human(context, params) -> ElicitResult:
    """The server needs the user's answer: show its question, read y or n."""
    answer = await anyio.to_thread.run_sync(input, f"\n{params.message} [y/n] ")
    return ElicitResult(action="accept", content={"confirm": answer.strip().lower() == "y"})


async def main() -> None:
    async with Client("http://127.0.0.1:8002/mcp", elicitation_callback=ask_the_human) as client:
        menu = await client.list_tools()
        for tool in menu.tools:
            print(f"{tool.name}: {tool.description}")

        product = await client.call_tool("get_product", {"product_id": 42})
        print("\nget_product:", product.content[0].text)

        order = await client.call_tool("place_order", {"product_id": 42, "quantity": 2})
        print("place_order:", order.content[0].text, "| is_error:", order.is_error)


anyio.run(main)
