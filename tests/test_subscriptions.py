"""Tests for pax8_get_subscription (PRD-21600).

Repo-first test file: there is no existing test convention here, so these
tests register the real subscriptions module against a FastMCP instance and
call the registered tool function directly (``Tool.fn``) -- the same
function object wired up for real MCP calls, not a reimplementation of its
logic. HTTP is mocked with respx at the httpx transport level, which works
regardless of ``Pax8Client`` opening a fresh ``httpx.AsyncClient`` per call.
"""

import json

import pytest
import respx
from httpx import Response
from mcp.server.fastmcp import FastMCP

from pax8_mcp.api_client import Pax8Client
from pax8_mcp.tools import subscriptions


def _get_subscription_tool(client_factory):
    mcp = FastMCP(name="test")
    subscriptions.register(mcp, client_factory)
    return mcp._tool_manager._tools["pax8_get_subscription"].fn


@pytest.mark.asyncio
@respx.mock
async def test_get_subscription_returns_pax8_response_verbatim():
    """TC1 / AC1."""
    body = {
        "id": "sub-123",
        "companyId": "company-456",
        "productId": "product-789",
        "quantity": 5,
        "status": "Active",
        "billingTerm": "Monthly",
        "startDate": "2026-01-01",
        "endDate": None,
        "price": 42.5,
    }
    respx.get("https://api.pax8.com/v1/subscriptions/sub-123").mock(
        return_value=Response(200, json=body)
    )
    client = Pax8Client(api_token="test-token")
    tool = _get_subscription_tool(lambda: client)

    result = await tool(subscription_id="sub-123")

    assert result == json.dumps(body, indent=2)


@pytest.mark.asyncio
@respx.mock
async def test_get_subscription_formats_pax8_error():
    """TC2 / AC2."""
    respx.get("https://api.pax8.com/v1/subscriptions/missing-id").mock(
        return_value=Response(404, json={"message": "Subscription not found"})
    )
    client = Pax8Client(api_token="test-token")
    tool = _get_subscription_tool(lambda: client)

    result = await tool(subscription_id="missing-id")

    assert result.startswith("Error 404:")


@pytest.mark.asyncio
async def test_get_subscription_without_credentials_returns_no_token_message():
    """TC3 / AC3. No respx mock registered: a real HTTP call would error out,
    so an unmodified test outcome also demonstrates no call was attempted."""
    tool = _get_subscription_tool(lambda: None)

    result = await tool(subscription_id="sub-123")

    assert result == subscriptions._NO_TOKEN
