import json
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

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

    @mcp.tool(
        annotations=ToolAnnotations(
            readOnlyHint=False, destructiveHint=True, idempotentHint=True,
        )
    )
    async def pax8_update_subscription(
        subscription_id: str,
        quantity: int,
        billing_term: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        price: float | None = None,
        partner_cost: float | None = None,
        currency_code: str | None = None,
        provisioning_details: list[dict[str, str]] | None = None,
    ) -> str:
        """Update a Pax8 subscription's quantity, billing term, or dates.

        This changes the customer's live subscription and billing in Pax8.
        Confirm the new quantity and terms with the requester before calling.
        Fields you omit keep their current value; only the fields you pass change.

        Args:
            subscription_id: The unique identifier of the subscription to update.
            quantity: New total seat/license count for the subscription.
            billing_term: One of: Monthly, Annual, 2-Year, 3-Year, 1-Time, Trial.
            start_date: New start date (ISO 8601, e.g. "2026-11-01").
            end_date: New end date (ISO 8601).
            price: New unit price.
            partner_cost: New partner cost.
            currency_code: ISO currency code, e.g. "USD".
            provisioning_details: List of {"key": ..., "value": ...} entries.
        """
        client = client_factory()
        if client is None:
            return _NO_TOKEN
        try:
            result = await client.put(
                f"/subscriptions/{subscription_id}",
                json_body={
                    "quantity": quantity,
                    "billingTerm": billing_term,
                    "startDate": start_date,
                    "endDate": end_date,
                    "price": price,
                    "partnerCost": partner_cost,
                    "currencyCode": currency_code,
                    "provisioningDetails": provisioning_details,
                },
            )
            return json.dumps(result, indent=2)
        except Pax8Error as e:
            return f"Error {e.status_code}: {e.message}"
