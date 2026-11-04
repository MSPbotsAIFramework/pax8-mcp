import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import Pax8Client, Pax8Error

_NO_TOKEN = "Error: No Pax8 token configured. Set PAX8_API_TOKEN or use AUTH_MODE=gateway."


def register(mcp: FastMCP, client_factory: Callable[[], Pax8Client | None]) -> None:
    @mcp.tool()
    async def pax8_list_companies(
        page: int = 0,
        size: int = 10,
        sort: str | None = None,
        name: str | None = None,
    ) -> str:
        """List companies in the Pax8 partner account.

        Args:
            page: Zero-based page number for pagination (default: 0).
            size: Number of results per page (default: 10).
            sort: Sort field and direction, e.g. "name,asc" or "createdDate,desc".
            name: Filter companies by name (partial match).
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.get(
                "/companies",
                params={"page": page, "size": size, "sort": sort, "name": name},
            )
            return json.dumps(result, indent=2)
        except Pax8Error as e:
            return f"Error {e.status_code}: {e.message}"

    @mcp.tool()
    async def pax8_list_company_contacts(
        company_id: str,
        page: int = 0,
        size: int = 10,
    ) -> str:
        """List contacts for a specific company.

        Args:
            company_id: The unique identifier of the company.
            page: Zero-based page number for pagination (default: 0).
            size: Number of results per page (default: 10).
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.get(
                f"/companies/{company_id}/contacts",
                params={"page": page, "size": size},
            )
            return json.dumps(result, indent=2)
        except Pax8Error as e:
            return f"Error {e.status_code}: {e.message}"

    @mcp.tool()
    async def pax8_get_company(company_id: str) -> str:
        """Get a single company by its Pax8 company id.

        Args:
            company_id: The unique identifier of the company.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.get(f"/companies/{company_id}")
            return json.dumps(result, indent=2)
        except Pax8Error as e:
            return f"Error {e.status_code}: {e.message}"
