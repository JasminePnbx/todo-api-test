import logging
from typing import Any
import requests
from client.api_client       import ApiClient
from client.schema_validator  import SchemaValidator, USER_SCHEMA
from client.response_assert   import ResponseAssert

logger = logging.getLogger(__name__)


class UserApi:
    _BASE = "/users"

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list_users(self) -> list[dict[str, Any]]:
        resp = self._client.get(self._BASE)
        body = ResponseAssert.of(resp).status(200).body()
        for user in body:
            SchemaValidator.assert_matches(user, USER_SCHEMA)
        return body

    def get_user(self, user_id: int) -> dict[str, Any]:
        resp = self._client.get(f"{self._BASE}/{user_id}")
        body = ResponseAssert.of(resp).status(200).body()
        SchemaValidator.assert_matches(body, USER_SCHEMA)
        return body

    def create_user(self, name: str, email: str,
                    role: str = "member") -> dict[str, Any]:
        payload = {"name": name, "email": email, "role": role}
        resp = self._client.post(self._BASE, body=payload)
        body = ResponseAssert.of(resp).status(201).body()
        SchemaValidator.assert_matches(body, USER_SCHEMA)
        logger.info("create_user | id=%s | email=%s", body["id"], email)
        return body

    def update_user(self, user_id: int, **fields) -> dict[str, Any]:
        resp = self._client.put(f"{self._BASE}/{user_id}", body=fields)
        body = ResponseAssert.of(resp).status(200).body()
        SchemaValidator.assert_matches(body, USER_SCHEMA)
        return body

    def delete_user(self, user_id: int) -> None:
        resp = self._client.delete(f"{self._BASE}/{user_id}")
        ResponseAssert.of(resp).status(204)

    # 负向操作：返回原始 Response 供测试断言错误码
    def try_get_user(self, user_id: int) -> requests.Response:
        return self._client.get(f"{self._BASE}/{user_id}")

    def try_create_user(self, payload: dict) -> requests.Response:
        return self._client.post(self._BASE, body=payload)