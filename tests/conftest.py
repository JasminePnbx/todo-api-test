import logging
import uuid
import pytest

from client.api_client import ApiClient
from api.user_api      import UserApi
from api.todo_api      import TodoApi
from config            import settings  # 核心：引入强类型配置
from tests.factories import UserPayloadFactory

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-8s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)

@pytest.fixture(scope="session")
def api_client():
    # 彻底告别 os.environ，享受 IDE 的代码补全吧！
    client = ApiClient(base_url=settings.base_url)
    yield client
    client.close()

@pytest.fixture(scope="session")
def user_api(api_client: ApiClient) -> UserApi:
    return UserApi(client=api_client)

@pytest.fixture(scope="session")
def todo_api(api_client: ApiClient) -> TodoApi:
    return TodoApi(client=api_client)

# ── 每个测试类共享的预置用户，避免每个测试都重复创建 ──────────────
@pytest.fixture(scope="class")
def existing_user(user_api: UserApi):
    payload = UserPayloadFactory() # 🌟 直接用工厂造数
    resp = user_api.create_user(**payload)
    user = resp.json()
    yield user
    try:
        user_api.delete_user(user["id"])
    except Exception:
        pass