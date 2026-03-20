import os
import logging
import pytest
from pathlib import Path
from dotenv import load_dotenv
from client.api_client import ApiClient
from api.user_api      import UserApi
from api.todo_api      import TodoApi

# 用 __file__ 定位 conftest.py 自身的位置，
# 再往上找项目根目录，确保无论从哪里运行都能找到 .env.test
_ROOT = Path(__file__).parent.parent   # tests/ -> todo_api_test/
load_dotenv(_ROOT / f".env.{os.getenv('ENV', 'test')}")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-8s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)


@pytest.fixture(scope="session")
def api_client():                    # type: ignore[return]
    client = ApiClient(base_url=os.environ["BASE_URL"])
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
def existing_user(user_api: UserApi) -> dict:
    """
    scope="class"：同一个测试类内共享一个预置用户。
    用 yield 保证测试结束后清理，不污染其他测试。
    """
    import uuid
    user = user_api.create_user(
        name="Fixture User",
        email=f"fixture_{uuid.uuid4().hex[:8]}@test.com",
    )
    yield user
    try:
        user_api.delete_user(user["id"])
    except Exception:
        pass