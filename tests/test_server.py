"""Server-level test for PRD-21602.

Covers TC-PAX8-004 (AC4): pax8_get_company is registered with a required
string company_id parameter, alongside the other 9 tools (10 total).
"""

from pax8_mcp.config import Settings
from pax8_mcp.server import create_mcp_server


async def test_tools_list_includes_pax8_get_company():
    settings = Settings(auth_mode="env", pax8_api_token="test-token")
    mcp = create_mcp_server(settings)

    tools = await mcp.list_tools()
    by_name = {t.name: t for t in tools}

    assert len(tools) == 10
    assert "pax8_get_company" in by_name

    schema = by_name["pax8_get_company"].inputSchema
    assert schema["required"] == ["company_id"]
    assert schema["properties"]["company_id"]["type"] == "string"
