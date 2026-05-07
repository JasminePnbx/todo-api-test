import logging
from typing import Any
import requests


class ResponseAssert:
    def __init__(self, response: requests.Response) -> None:
        self._resp = response
        try:
            self._body: Any = response.json()
        except Exception:
            self._body = {}

    @classmethod
    def of(cls, response: requests.Response) -> "ResponseAssert":
        return cls(response)

    def status(self, expected: int) -> "ResponseAssert":
        actual = self._resp.status_code
        assert actual == expected, (
            f"状态码错误 | expected={expected} actual={actual} | body={self._body}"
        )
        return self

    def has_key(self, key: str) -> "ResponseAssert":
        assert key in self._body, (
            f"缺少字段 '{key}' | keys={list(self._body.keys())}"
        )
        return self

    def field_equals(self, key: str, expected: Any) -> "ResponseAssert":
        actual = self._body.get(key)
        assert actual == expected, (
            f"字段值错误 | '{key}' expected={expected!r} actual={actual!r}"
        )
        return self

    def body(self) -> Any:
        return self._body