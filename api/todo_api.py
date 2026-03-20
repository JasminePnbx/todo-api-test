import logging
from typing import Any, Optional
import requests
from client.api_client       import ApiClient
from client.schema_validator  import SchemaValidator, TODO_SCHEMA
from client.response_assert   import ResponseAssert

logger = logging.getLogger(__name__)


class TodoApi:
    _BASE = "/todos"

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list_todos(self, user_id: Optional[int] = None) -> list[dict[str, Any]]:
        params = {"user_id": user_id} if user_id else None
        resp = self._client.get(self._BASE, params=params)
        body = ResponseAssert.of(resp).status(200).body()
        for todo in body:
            SchemaValidator.assert_matches(todo, TODO_SCHEMA)
        return body

    def create_todo(self, title: str, user_id: int) -> dict[str, Any]:
        payload = {"title": title, "user_id": user_id}
        resp = self._client.post(self._BASE, body=payload)
        body = ResponseAssert.of(resp).status(201).body()
        SchemaValidator.assert_matches(body, TODO_SCHEMA)
        logger.info("create_todo | id=%s | user_id=%s", body["id"], user_id)
        return body

    def complete_todo(self, todo_id: int) -> dict[str, Any]:
        resp = self._client.patch(f"{self._BASE}/{todo_id}",
                                  body={"completed": True})
        body = ResponseAssert.of(resp).status(200).body()
        return body

    def delete_todo(self, todo_id: int) -> None:
        resp = self._client.delete(f"{self._BASE}/{todo_id}")
        ResponseAssert.of(resp).status(204)

    def try_create_todo(self, payload: dict) -> requests.Response:
        return self._client.post(self._BASE, body=payload)