from typing import Any

import httpx

DEFAULT_BASE_URL = "https://api.pax8.com/v1"
DEFAULT_AUTH_HEADER = "X-Pax8-Token"


class Pax8Error(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Pax8 API error {status_code}: {message}")


class Pax8Client:
    """Async httpx client wrapping the Pax8 REST API.

    Accepts a raw access token and sends it as a Bearer token
    in the Authorization header on every API request.
    """

    def __init__(
        self,
        api_token: str,
        base_url: str = DEFAULT_BASE_URL,
        auth_header: str = DEFAULT_AUTH_HEADER,
    ):
        self._token = api_token
        self._base_url = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def _clean_params(self, params: dict | None) -> dict:
        if not params:
            return {}
        return {k: v for k, v in params.items() if v is not None}

    async def get(self, path: str, params: dict | None = None) -> Any:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._base_url}{path}",
                headers=self._headers(),
                params=self._clean_params(params),
            )
            self._raise_for_status(resp)
            return resp.json() if resp.status_code != 204 else None

    async def put(self, path: str, json_body: dict | None = None) -> Any:
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self._base_url}{path}",
                headers=self._headers(),
                json=self._clean_params(json_body),
            )
            self._raise_for_status(resp)
            return resp.json() if resp.status_code != 204 else None

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise Pax8Error(resp.status_code, str(detail))
