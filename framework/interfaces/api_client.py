# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring

import json as _json_module
from playwright.sync_api import APIRequestContext


class APIClient:
    """
    Thin wrapper around Playwright's APIRequestContext

    Each method returns a _PlaywrightResponse object that exposes:
        .status_code  - HTTP status code (int)
        .text         - raw response body (str)
        .json()       - parsed JSON body (dict / list)
        .headers      - response headers (dict)
    """

    def __init__(self, request_context: APIRequestContext, base_url: str, headers: dict = None):
        self._ctx = request_context
        self.base_url = base_url.rstrip("/")
        self._headers = headers or {}

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    def _merge_headers(self, extra: dict) -> dict:
        return {**self._headers, **extra}

    # ------------------------------------------------------------------
    # HTTP verbs
    # ------------------------------------------------------------------

    def get(self, endpoint: str, **kwargs):
        extra_headers = kwargs.pop("headers", {})
        response = self._ctx.get(
            f"{self.base_url}{endpoint}",
            headers=self._merge_headers(extra_headers),
            **kwargs,
        )
        return _PlaywrightResponse(response)

    def post(self, endpoint: str, data=None, json=None, **kwargs):
        extra_headers = kwargs.pop("headers", {})
        headers = self._merge_headers(extra_headers)
        if json is not None:
            headers.setdefault("Content-Type", "application/json; charset=UTF-8")
            response = self._ctx.post(
                f"{self.base_url}{endpoint}",
                headers=headers,
                data=_json_module.dumps(json),
                **kwargs,
            )
        else:
            response = self._ctx.post(
                f"{self.base_url}{endpoint}",
                headers=headers,
                data=data,
                **kwargs,
            )
        return _PlaywrightResponse(response)

    def put(self, endpoint: str, data=None, json=None, **kwargs):
        extra_headers = kwargs.pop("headers", {})
        headers = self._merge_headers(extra_headers)
        if json is not None:
            headers.setdefault("Content-Type", "application/json; charset=UTF-8")
            response = self._ctx.put(
                f"{self.base_url}{endpoint}",
                headers=headers,
                data=_json_module.dumps(json),
                **kwargs,
            )
        else:
            response = self._ctx.put(
                f"{self.base_url}{endpoint}",
                headers=headers,
                data=data,
                **kwargs,
            )
        return _PlaywrightResponse(response)

    def patch(self, endpoint: str, data=None, json=None, **kwargs):
        extra_headers = kwargs.pop("headers", {})
        headers = self._merge_headers(extra_headers)
        if json is not None:
            headers.setdefault("Content-Type", "application/json; charset=UTF-8")
            response = self._ctx.patch(
                f"{self.base_url}{endpoint}",
                headers=headers,
                data=_json_module.dumps(json),
                **kwargs,
            )
        else:
            response = self._ctx.patch(
                f"{self.base_url}{endpoint}",
                headers=headers,
                data=data,
                **kwargs,
            )
        return _PlaywrightResponse(response)

    def delete(self, endpoint: str, **kwargs):
        extra_headers = kwargs.pop("headers", {})
        response = self._ctx.delete(
            f"{self.base_url}{endpoint}",
            headers=self._merge_headers(extra_headers),
            **kwargs,
        )
        return _PlaywrightResponse(response)


class _PlaywrightResponse:
    """
    Adapter that makes a Playwright APIResponse look like a requests.Response
    """

    def __init__(self, pw_response):
        self._response = pw_response
        self.status_code: int = pw_response.status
        self.headers: dict = dict(pw_response.headers)
        self.text: str = pw_response.text()

    def json(self):
        return self._response.json()

    def __repr__(self):
        return f"<PlaywrightResponse [{self.status_code}]>"
