import asyncio

import httpx
import pytest
import respx
from mcp.server.fastmcp.exceptions import ToolError

from pax8_mcp.config import Settings
from pax8_mcp.server import _gateway_token_var, create_mcp_server

BASE_URL = "https://api.pax8.com/v1"

PRODUCT_RESPONSE = {
    "id": "prod-123",
    "name": "Microsoft 365 Business Premium",
    "vendorName": "Microsoft",
    "shortDescription": "M365 Business Premium seat",
    "sku": "CFQ7TTC0LH18",
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


@respx.mock
async def test_get_product_returns_pax8_record(mcp):
    """TC-PAX8-001 / AC1"""
    respx.get(f"{BASE_URL}/products/prod-123").mock(
        return_value=httpx.Response(200, json=PRODUCT_RESPONSE)
    )

    result = await _call_with_token(
        mcp, "tenant-a-token", "pax8_get_product", {"product_id": "prod-123"}
    )

    text = _text(result)
    assert '"id": "prod-123"' in text
    assert '"name": "Microsoft 365 Business Premium"' in text
    assert '"vendorName": "Microsoft"' in text
    assert '"shortDescription": "M365 Business Premium seat"' in text
    assert '"sku": "CFQ7TTC0LH18"' in text


@respx.mock
async def test_get_product_passes_through_404(mcp):
    """TC-PAX8-002 / AC2"""
    respx.get(f"{BASE_URL}/products/missing-id").mock(
        return_value=httpx.Response(404, json={"message": "Product not found"})
    )

    result = await _call_with_token(
        mcp, "tenant-a-token", "pax8_get_product", {"product_id": "missing-id"}
    )

    text = _text(result)
    assert text.startswith("Error 404:")
    assert "Product not found" in text


@respx.mock
async def test_get_product_error_does_not_leak_token(mcp):
    """TC-PAX8-003 / AC2"""
    respx.get(f"{BASE_URL}/products/prod-500").mock(
        return_value=httpx.Response(500, json={"message": "Internal error"})
    )

    result = await _call_with_token(
        mcp, "super-secret-token", "pax8_get_product", {"product_id": "prod-500"}
    )

    text = _text(result)
    assert text.startswith("Error 500:")
    assert "super-secret-token" not in text


async def test_get_product_without_credentials(mcp):
    """TC-PAX8-004 / AC3"""
    with respx.mock(assert_all_called=False) as mock:
        route = mock.get(f"{BASE_URL}/products/prod-123")
        # No contextvar token set -> client_factory() must return None before any HTTP call.
        result = await mcp.call_tool("pax8_get_product", {"product_id": "prod-123"})
        assert not route.called

    text = _text(result)
    assert text == "Error: No Pax8 token configured. Set PAX8_API_TOKEN or use AUTH_MODE=gateway."


async def test_get_product_requires_product_id(mcp):
    """TC-PAX8-005 / AC4"""
    with respx.mock(assert_all_called=False) as mock:
        route = mock.get(url__regex=rf"{BASE_URL}/products/.*")
        with pytest.raises(ToolError):
            await mcp.call_tool("pax8_get_product", {})
        assert not route.called


async def test_get_product_concurrent_requests_do_not_share_token(mcp):
    """TC-PAX8-006 / AC5"""
    with respx.mock(assert_all_called=False) as mock:
        mock.get(f"{BASE_URL}/products/prod-a").mock(
            return_value=httpx.Response(200, json={"id": "prod-a"})
        )
        mock.get(f"{BASE_URL}/products/prod-b").mock(
            return_value=httpx.Response(200, json={"id": "prod-b"})
        )

        await asyncio.gather(
            _call_with_token(mcp, "tenant-a-token", "pax8_get_product", {"product_id": "prod-a"}),
            _call_with_token(mcp, "tenant-b-token", "pax8_get_product", {"product_id": "prod-b"}),
        )

        calls_by_path = {
            call.request.url.path: call.request.headers.get("authorization")
            for call in mock.calls
        }

    assert calls_by_path["/v1/products/prod-a"] == "Bearer tenant-a-token"
    assert calls_by_path["/v1/products/prod-b"] == "Bearer tenant-b-token"
