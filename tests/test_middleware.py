import asyncio

import httpx
import respx

from pax8_mcp.__main__ import _build_http_app
from pax8_mcp.config import Settings
from pax8_mcp.server import create_mcp_server

from .conftest import lifespan_running

BASE_URL = "https://api.pax8.com/v1"
MCP_HEADERS = {"Accept": "application/json, text/event-stream"}


def _make_app():
    settings = Settings(auth_mode="gateway")
    mcp = create_mcp_server(settings)
    return _build_http_app(mcp, settings)


async def test_missing_header_returns_401_on_mcp_endpoint():
    app = _make_app()
    async with lifespan_running(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as http:
            resp = await http.post(
                "/mcp",
                json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                headers=MCP_HEADERS,
            )

    assert resp.status_code == 401
    body = resp.json()
    assert body["required_headers"] == ["X-Pax8-Token"]


async def test_health_endpoint_does_not_require_credentials():
    app = _make_app()
    async with lifespan_running(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as http:
            resp = await http.get("/health")

    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_concurrent_update_calls_do_not_leak_credentials_across_tenants():
    app = _make_app()

    async def call_tool(http: httpx.AsyncClient, subscription_id: str, token: str):
        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "pax8_update_subscription",
                "arguments": {"subscription_id": subscription_id, "quantity": 5},
            },
        }
        return await http.post(
            "/mcp", json=body, headers={**MCP_HEADERS, "X-Pax8-Token": token}
        )

    async with lifespan_running(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as http:
            with respx.mock(assert_all_called=False) as mock:
                mock.put(f"{BASE_URL}/subscriptions/sub-a").mock(
                    return_value=httpx.Response(200, json={"id": "sub-a"})
                )
                mock.put(f"{BASE_URL}/subscriptions/sub-b").mock(
                    return_value=httpx.Response(200, json={"id": "sub-b"})
                )

                resp_a, resp_b = await asyncio.gather(
                    call_tool(http, "sub-a", "tenant-a-token"),
                    call_tool(http, "sub-b", "tenant-b-token"),
                )

                assert resp_a.status_code == 200
                assert resp_b.status_code == 200

                calls_by_path = {
                    call.request.url.path: call.request.headers.get("authorization")
                    for call in mock.calls
                }

    assert calls_by_path["/v1/subscriptions/sub-a"] == "Bearer tenant-a-token"
    assert calls_by_path["/v1/subscriptions/sub-b"] == "Bearer tenant-b-token"
