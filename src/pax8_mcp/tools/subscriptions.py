import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import Pax8Client, Pax8Error

_NO_TOKEN = "Error: No Pax8 token configured. Set PAX8_API_TOKEN or use AUTH_MODE=gateway."


def register(mcp: FastMCP, client_factory: Callable[[], Pax8Client | None]) -> None:
    @mcp.tool()
    async def pax8_list_subscriptions(
        page: int = 0,
        size: int = 10,
        sort: str | None = None,
        company_id: str | None = None,
        status: str | None = None,
        product_id: str | None = None,
    ) -> str:
        """List subscriptions in the Pax8 partner account.

        Args:
            page: Zero-based page number for pagination (default: 0).
            size: Number of results per page (default: 10).
            sort: Sort field and direction, e.g. "startDate,asc".
            company_id: Filter by company ID.
            status: Filter by subscription status. One of: Active, Cancelled,
                PendingManual, PendingAutomated, PendingCancel, Terminated, Expired, Trial.
            product_id: Filter by product ID.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.get(
                "/subscriptions",
                params={
                    "page": page,
                    "size": size,
                    "sort": sort,
                    "companyId": company_id,
                    "status": status,
                    "productId": product_id,
                },
            )
            return json.dumps(result, indent=2)
        except Pax8Error as e:
            return f"Error {e.status_code}: {e.message}"

    @mcp.tool()
    async def pax8_get_subscription(subscription_id: str) -> str:
        """Get a single Pax8 subscription by id.

        Args:
            subscription_id: The unique identifier of the subscription.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.get(f"/subscriptions/{subscription_id}")
            return json.dumps(result, indent=2)
        except Pax8Error as e:
            return f"Error {e.status_code}: {e.message}"

    @mcp.tool()
    async def pax8_list_subscription_usage_summaries(
        subscription_id: str,
        page: int = 0,
        size: int = 10,
    ) -> str:
        """List usage summaries for a specific subscription.

        Args:
            subscription_id: The unique identifier of the subscription.
            page: Zero-based page number for pagination (default: 0).
            size: Number of results per page (default: 10).
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.get(
                f"/subscriptions/{subscription_id}/usage-summaries",
                params={"page": page, "size": size},
            )
            return json.dumps(result, indent=2)
        except Pax8Error as e:
            return f"Error {e.status_code}: {e.message}"
