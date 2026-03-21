import logging
from client.api_client import ApiClient
import requests

logger = logging.getLogger(__name__)


class UserApi:
    _BASE = "/users"

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def list_users(self) -> requests.Response:
        logger.info("list_users")
        return self._client.get(self._BASE)

    def get_user(self, user_id: int) -> requests.Response:
        logger.info("get_user | id=%d", user_id)
        return self._client.get(f"{self._BASE}/{user_id}")

    def create_user(self, name: str, email: str,
                    role: str = "member") -> requests.Response:
        payload = {"name": name, "email": email, "role": role}
        logger.info("create_user | email=%s", email)
        return self._client.post(self._BASE, body=payload)

    def update_user(self, user_id: int, **fields) -> requests.Response:
        logger.info("update_user | id=%d | fields=%s", user_id, fields)
        return self._client.put(f"{self._BASE}/{user_id}", body=fields)

    def delete_user(self, user_id: int) -> requests.Response:
        logger.info("delete_user | id=%d", user_id)
        return self._client.delete(f"{self._BASE}/{user_id}")