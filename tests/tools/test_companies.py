"""Tests for pax8_get_company (PRD-21602).

Covers TC-PAX8-001 (AC1), TC-PAX8-002 (AC2), TC-PAX8-003 (AC3).
"""

import respx
from httpx import Response
from mcp.server.fastmcp import FastMCP

from pax8_mcp.api_client import Pax8Client
from pax8_mcp.tools import companies

BASE_URL = "https://api.pax8.com/v1"


def _build_mcp(client_factory):
    mcp = FastMCP(name="pax8-mcp-test")
    companies.register(mcp, client_factory)
    return mcp


async def _call(mcp: FastMCP, name: str, arguments: dict) -> str:
    """Call a registered tool and return its plain-text result."""
    blocks, _structured = await mcp.call_tool(name, arguments)
    return blocks[0].text


@respx.mock
async def test_pax8_get_company_returns_company_json():
    company = {"id": "comp-1", "name": "Acme Co", "status": "Active", "externalId": "ext-1"}
    respx.get(f"{BASE_URL}/companies/comp-1").mock(return_value=Response(200, json=company))

    mcp = _build_mcp(lambda: Pax8Client("test-token"))
    result = await _call(mcp, "pax8_get_company", {"company_id": "comp-1"})

    assert '"id": "comp-1"' in result
    assert '"name": "Acme Co"' in result
    assert '"status": "Active"' in result
    assert '"externalId": "ext-1"' in result


@respx.mock
async def test_pax8_get_company_not_found_returns_structured_error():
    respx.get(f"{BASE_URL}/companies/missing").mock(
        return_value=Response(404, json={"message": "not found"})
    )

    mcp = _build_mcp(lambda: Pax8Client("test-token"))
    result = await _call(mcp, "pax8_get_company", {"company_id": "missing"})

    assert result.startswith("Error 404:")


async def test_pax8_get_company_no_token_returns_diagnostic_message():
    mcp = _build_mcp(lambda: None)
    result = await _call(mcp, "pax8_get_company", {"company_id": "comp-1"})

    assert result == companies._NO_TOKEN
