import pytest
from client.api_client import ApiClient
from api.user_api import UserApi
from api.todo_api import TodoApi
from config import settings
from utils.factories import UserPayloadFactory   # 注意：factories 还在 tests/ 下，稍后我们会移动它，但先保持原样

# 不再需要 logging.basicConfig，由 utils.logger 接管

@pytest.fixture(scope="session")
def api_client():
    client = ApiClient(base_url=settings.base_url)
    yield client
    client.close()

@pytest.fixture(scope="session")
def user_api(api_client: ApiClient) -> UserApi:
    return UserApi(client=api_client)

@pytest.fixture(scope="session")
def todo_api(api_client: ApiClient) -> TodoApi:
    return TodoApi(client=api_client)

@pytest.fixture(scope="class")
def existing_user(user_api: UserApi):
    payload = UserPayloadFactory()
    resp = user_api.create_user(**payload)
    user = resp.json()
    yield user
    try:
        user_api.delete_user(user["id"])
    except Exception:
        pass