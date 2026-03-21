import logging
from typing import Optional
from client.api_client import ApiClient
import requests

logger = logging.getLogger(__name__)


class TodoApi:
    _BASE = "/todos"

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list_todos(self, user_id: Optional[int] = None) -> requests.Response:
        params = {"user_id": user_id} if user_id else None
        logger.info("list_todos | user_id=%s", user_id)
        return self._client.get(self._BASE, params=params)

    def create_todo(self, title: str, user_id: int) -> requests.Response:
        payload = {"title": title, "user_id": user_id}
        logger.info("create_todo | title=%s | user_id=%d", title, user_id)
        return self._client.post(self._BASE, body=payload)

    def complete_todo(self, todo_id: int) -> requests.Response:
        logger.info("complete_todo | id=%d", todo_id)
        return self._client.patch(
            f"{self._BASE}/{todo_id}",
            body={"completed": True}
        )

    def delete_todo(self, todo_id: int) -> requests.Response:
        logger.info("delete_todo | id=%d", todo_id)
        return self._client.delete(f"{self._BASE}/{todo_id}")