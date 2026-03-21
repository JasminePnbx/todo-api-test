# tests/test_db_validation.py
"""
数据库验证测试。
每个用例做两层断言：
    第一层：HTTP 响应正确（接口层）
    第二层：数据库记录正确（存储层）
这是大多数同学没有的测试维度，能发现"接口返回成功但数据没写进去"的 bug。
"""
import uuid
import pytest
from api.user_api import UserApi
from api.todo_api import TodoApi
from tests.db_helper import (
    get_user_from_db,
    get_todo_from_db,
    user_exists_in_db,
    count_users_in_db,
)


def unique_email() -> str:
    return f"dbtest_{uuid.uuid4().hex[:8]}@example.com"


class TestUserDatabaseValidation:

    def test_create_user_persisted_to_database(self, user_api: UserApi) -> None:
        """
        核心验证：POST /users 成功后，数据真的写进数据库了吗？
        这个用例能发现"接口返回 201 但数据库没写入"的 bug。
        """
        resp = user_api.create_user(name="DB Test User", email=unique_email())
        assert resp.status_code == 201
        user_id = resp.json()["id"]

        # ── 第二层：直接查数据库 ──────────────────────────────
        db_record = get_user_from_db(user_id)

        assert db_record is not None,         "用户应已写入数据库，但查不到记录"
        assert db_record["name"]  == "DB Test User"
        assert db_record["email"] == resp.json()["email"]
        assert db_record["role"]  == "member"

    def test_update_user_persisted_to_database(self, user_api: UserApi) -> None:
        """
        PUT /users/{id} 之后，数据库里的记录真的更新了吗？
        """
        create_resp = user_api.create_user(name="Before Update", email=unique_email())
        user_id = create_resp.json()["id"]

        user_api.update_user(user_id, name="After Update")

        # ── 直接查数据库，验证更新落地 ───────────────────────
        db_record = get_user_from_db(user_id)
        assert db_record["name"] == "After Update", (
            f"数据库记录应已更新，实际: {db_record['name']!r}"
        )

    def test_delete_user_removed_from_database(self, user_api: UserApi) -> None:
        """
        DELETE /users/{id} 之后，数据库里的记录真的删除了吗？
        这是"操作后状态验证"的数据库版本。
        """
        create_resp = user_api.create_user(name="To Delete", email=unique_email())
        user_id = create_resp.json()["id"]

        # 确认创建后数据库里有这条记录
        assert user_exists_in_db(user_id) is True

        user_api.delete_user(user_id)

        # ── 直接查数据库，验证记录已删除 ─────────────────────
        assert user_exists_in_db(user_id) is False, (
            "删除接口返回成功，但数据库记录仍然存在"
        )

    def test_database_count_increases_after_create(self, user_api: UserApi) -> None:
        """
        创建用户后，数据库总数应该 +1。
        验证数据库的计数层面是否正确。
        """
        count_before = count_users_in_db()

        user_api.create_user(name="Count Test", email=unique_email())

        count_after = count_users_in_db()
        assert count_after == count_before + 1, (
            f"预期数据库用户数 +1，实际: {count_before} → {count_after}"
        )

    def test_http_response_matches_database_record(self, user_api: UserApi) -> None:
        """
        接口响应和数据库记录一致性验证：
        接口返回的数据和数据库存储的数据完全一致。
        防止"接口响应正确但存储了不同的值"这种数据不一致 bug。
        """
        email = unique_email()
        resp = user_api.create_user(name="Consistency Test", email=email, role="admin")
        assert resp.status_code == 201

        api_data = resp.json()
        db_data  = get_user_from_db(api_data["id"])

        assert db_data is not None
        assert api_data["name"]  == db_data["name"],  "接口响应 name 与数据库不一致"
        assert api_data["email"] == db_data["email"], "接口响应 email 与数据库不一致"
        assert api_data["role"]  == db_data["role"],  "接口响应 role 与数据库不一致"


class TestTodoDatabaseValidation:

    @pytest.fixture(scope="class")
    def db_test_user(self, user_api: UserApi) -> dict:   # type: ignore[return]
        """数据库验证测试专用用户。"""
        resp = user_api.create_user(
            name="DB Todo Owner",
            email=f"db_todo_{uuid.uuid4().hex[:6]}@test.com",
        )
        user = resp.json()
        yield user
        user_api.delete_user(user["id"])

    def test_create_todo_persisted_to_database(
        self, todo_api: TodoApi, db_test_user: dict
    ) -> None:
        """POST /todos 之后，数据库里真的有这条 Todo 记录吗？"""
        resp = todo_api.create_todo(
            title="DB Persisted Task", user_id=db_test_user["id"]
        )
        assert resp.status_code == 201
        todo_id = resp.json()["id"]

        db_record = get_todo_from_db(todo_id)

        assert db_record is not None,              "Todo 应已写入数据库"
        assert db_record["title"]     == "DB Persisted Task"
        assert db_record["user_id"]   == db_test_user["id"]
        assert db_record["completed"] is False

    def test_complete_todo_updated_in_database(
        self, todo_api: TodoApi, db_test_user: dict
    ) -> None:
        """PATCH /todos/{id} 标记完成后，数据库里 completed 字段真的变 True 了吗？"""
        create_resp = todo_api.create_todo(
            title="Will Complete", user_id=db_test_user["id"]
        )
        todo_id = create_resp.json()["id"]

        todo_api.complete_todo(todo_id)

        db_record = get_todo_from_db(todo_id)
        assert db_record["completed"] is True, (
            "数据库里 completed 应为 True，但实际为 False"
        )

