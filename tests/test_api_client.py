import httpx
import pytest
import respx

from pax8_mcp.api_client import Pax8Client, Pax8Error

BASE_URL = "https://api.pax8.com/v1"


@pytest.fixture
def client() -> Pax8Client:
    return Pax8Client(api_token="test-token", base_url=BASE_URL)


@respx.mock
async def test_put_sends_request_and_returns_result(client: Pax8Client):
    route = respx.put(f"{BASE_URL}/subscriptions/sub1").mock(
        return_value=httpx.Response(
            200,
            json={"id": "sub1", "quantity": 25, "status": "Active", "billingTerm": "Monthly"},
        )
    )

    result = await client.put("/subscriptions/sub1", json_body={"quantity": 25})

    assert route.called
    assert result == {"id": "sub1", "quantity": 25, "status": "Active", "billingTerm": "Monthly"}
    sent = route.calls.last.request
    assert sent.headers["Authorization"] == "Bearer test-token"
    assert sent.headers["Content-Type"] == "application/json"


@respx.mock
async def test_put_omits_none_fields_from_json_body(client: Pax8Client):
    route = respx.put(f"{BASE_URL}/subscriptions/sub1").mock(
        return_value=httpx.Response(200, json={"id": "sub1"})
    )

    await client.put(
        "/subscriptions/sub1",
        json_body={
            "quantity": 25,
            "billingTerm": None,
            "startDate": None,
            "endDate": None,
            "price": None,
            "partnerCost": None,
            "currencyCode": None,
            "provisioningDetails": None,
        },
    )

    sent = route.calls.last.request
    assert sent.content == b'{"quantity":25}'


@respx.mock
async def test_put_raises_pax8_error_on_non_2xx(client: Pax8Client):
    respx.put(f"{BASE_URL}/subscriptions/bad-id").mock(
        return_value=httpx.Response(404, json={"message": "Subscription not found"})
    )

    with pytest.raises(Pax8Error) as exc_info:
        await client.put("/subscriptions/bad-id", json_body={"quantity": 25})

    assert exc_info.value.status_code == 404
    assert "Subscription not found" in exc_info.value.message
