"""Server-level test for PRD-21602.

Covers TC-PAX8-004 (AC4): pax8_get_company is registered with a required
string company_id parameter. The exact total tool count here tracks whatever
else is registered on this branch after syncing with the default branch
(13 at the time this ticket was merged: the original 9, PRD-21602's
pax8_get_company, and 3 more added by PRD-21600/PRD-21601); see tests/test_tools.py
for the authoritative full-registry snapshot.
"""

from pax8_mcp.config import Settings
from pax8_mcp.server import create_mcp_server


async def test_tools_list_includes_pax8_get_company():
    settings = Settings(auth_mode="env", pax8_api_token="test-token")
    mcp = create_mcp_server(settings)

    tools = await mcp.list_tools()
    by_name = {t.name: t for t in tools}

    assert len(tools) == 13
    assert "pax8_get_company" in by_name

    schema = by_name["pax8_get_company"].inputSchema
    assert schema["required"] == ["company_id"]
    assert schema["properties"]["company_id"]["type"] == "string"
