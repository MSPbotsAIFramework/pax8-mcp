import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import Pax8Client, Pax8Error

_NO_TOKEN = "Error: No Pax8 token configured. Set PAX8_API_TOKEN or use AUTH_MODE=gateway."


def register(mcp: FastMCP, client_factory: Callable[[], Pax8Client | None]) -> None:
    @mcp.tool()
    async def pax8_list_products(
        page: int = 0,
        size: int = 10,
        sort: str | None = None,
        vendor_name: str | None = None,
        product_name: str | None = None,
    ) -> str:
        """List products available in the Pax8 marketplace.

        Args:
            page: Zero-based page number for pagination (default: 0).
            size: Number of results per page (default: 10).
            sort: Sort field and direction, e.g. "productName,asc".
            vendor_name: Filter by vendor name (partial match).
            product_name: Filter by product name (partial match).
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.get(
                "/products",
                params={
                    "page": page,
                    "size": size,
                    "sort": sort,
                    "vendorName": vendor_name,
                    "productName": product_name,
                },
            )
            return json.dumps(result, indent=2)
        except Pax8Error as e:
            return f"Error {e.status_code}: {e.message}"

    @mcp.tool()
    async def pax8_get_product(product_id: str) -> str:
        """Get a single product by id.

        Args:
            product_id: The unique identifier of the product.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.get(f"/products/{product_id}")
            return json.dumps(result, indent=2)
        except Pax8Error as e:
            return f"Error {e.status_code}: {e.message}"
