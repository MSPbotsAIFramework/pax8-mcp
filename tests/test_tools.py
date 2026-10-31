import httpx
import pytest
import respx

from pax8_mcp.config import Settings
from pax8_mcp.server import _gateway_token_var, create_mcp_server

BASE_URL = "https://api.pax8.com/v1"

EXPECTED_TOOL_NAMES = {
    "pax8_list_companies",
    "pax8_list_company_contacts",
    "pax8_list_subscriptions",
    "pax8_list_subscription_usage_summaries",
    "pax8_update_subscription",
    "pax8_list_invoices",
    "pax8_list_invoice_items",
    "pax8_list_orders",
    "pax8_list_products",
    "pax8_get_product",
    "pax8_list_usage_summary_lines",
}


@pytest.fixture
def mcp():
    return create_mcp_server(Settings(auth_mode="gateway"))


async def _call_with_token(mcp, token, tool_name, arguments):
    ctx_token = _gateway_token_var.set(token)
    try:
        return await mcp.call_tool(tool_name, arguments)
    finally:
        _gateway_token_var.reset(ctx_token)


def _text(result) -> str:
    content, _ = result
    return content[0].text


async def test_tools_list_snapshot_includes_update_subscription(mcp):
    tools = await mcp.list_tools()

    names = {t.name for t in tools}
    assert names == EXPECTED_TOOL_NAMES
    assert len(tools) == 11
    for tool in tools:
        assert tool.description, f"{tool.name} is missing a description"

    update_tool = next(t for t in tools if t.name == "pax8_update_subscription")
    required = update_tool.inputSchema.get("required", [])
    assert set(required) == {"subscription_id", "quantity"}


@respx.mock
async def test_update_subscription_sends_put_and_returns_updated_subscription(mcp):
    route = respx.put(f"{BASE_URL}/subscriptions/sub-123").mock(
        return_value=httpx.Response(
            200,
            json={"id": "sub-123", "quantity": 25, "status": "Active", "billingTerm": "Monthly"},
        )
    )

    result = await _call_with_token(
        mcp,
        "tenant-a-token",
        "pax8_update_subscription",
        {"subscription_id": "sub-123", "quantity": 25, "billing_term": "Monthly"},
    )

    assert route.called
    text = _text(result)
    assert '"id": "sub-123"' in text
    assert '"quantity": 25' in text
    assert '"status": "Active"' in text
    assert '"billingTerm": "Monthly"' in text


async def test_update_subscription_without_credentials_returns_no_token_message(mcp):
    with respx.mock(assert_all_called=False) as mock:
        route = mock.put(f"{BASE_URL}/subscriptions/sub-123")
        # No contextvar token set -> client_factory() must return None before any HTTP call.
        result = await mcp.call_tool(
            "pax8_update_subscription", {"subscription_id": "sub-123", "quantity": 25}
        )
        assert not route.called

    text = _text(result)
    assert text == "Error: No Pax8 token configured. Set PAX8_API_TOKEN or use AUTH_MODE=gateway."


@respx.mock
async def test_update_subscription_maps_pax8_error_to_existing_error_format(mcp):
    respx.put(f"{BASE_URL}/subscriptions/unknown-id").mock(
        return_value=httpx.Response(404, json={"message": "Subscription not found"})
    )

    result = await _call_with_token(
        mcp,
        "tenant-a-token",
        "pax8_update_subscription",
        {"subscription_id": "unknown-id", "quantity": 25},
    )

    text = _text(result)
    assert text.startswith("Error 404:")
    assert "Subscription not found" in text
