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

env_file = f".env.{os.getenv('ENV', 'test')}"   # 例如 .env.test
env_path = _ROOT / env_file                     # 完整路径

# 加载该文件
load_dotenv(env_path)

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
def existing_user(user_api: UserApi):          # type: ignore[return]
    import uuid
    resp = user_api.create_user(
        name="Fixture User",
        email=f"fixture_{uuid.uuid4().hex[:8]}@test.com",
    )
    user = resp.json()                         # ← 加这一行，把 Response 转成 dict
    yield user
    try:
        user_api.delete_user(user["id"])
    except Exception:
        pass