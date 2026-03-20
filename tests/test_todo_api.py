import uuid
import pytest
from api.user_api import UserApi
from api.todo_api import TodoApi
from client.response_assert import ResponseAssert


@pytest.fixture(scope="module")
def test_user(user_api: UserApi) -> dict:             # type: ignore[return]
    """Todo 测试专用用户，整个 module 共享。"""
    user = user_api.create_user(
        name="Todo Owner",
        email=f"todo_owner_{uuid.uuid4().hex[:6]}@test.com",
    )
    yield user
    try:
        user_api.delete_user(user["id"])
    except Exception:
        pass


class TestCreateTodo:

    def test_create_todo_returns_correct_fields(
        self, todo_api: TodoApi, test_user: dict
    ) -> None:
        todo = todo_api.create_todo(title="Buy milk", user_id=test_user["id"])
        assert todo["title"]     == "Buy milk"
        assert todo["user_id"]   == test_user["id"]
        assert todo["completed"] is False            # 新建默认未完成

    def test_create_todo_for_nonexistent_user_returns_404(
        self, todo_api: TodoApi
    ) -> None:
        """
        跨资源约束验证：Todo 的 user_id 必须指向真实存在的用户。
        这是外键约束场景，面试中可以重点描述。
        """
        resp = todo_api.try_create_todo({"title": "Ghost Todo", "user_id": 999999})
        ResponseAssert.of(resp).status(404)


class TestCompleteTodo:

    def test_complete_todo_sets_flag_true(
        self, todo_api: TodoApi, test_user: dict
    ) -> None:
        todo = todo_api.create_todo(
            title="Task to complete", user_id=test_user["id"]
        )
        updated = todo_api.complete_todo(todo["id"])
        assert updated["completed"] is True

    def test_complete_already_completed_is_idempotent(
        self, todo_api: TodoApi, test_user: dict
    ) -> None:
        """
        幂等性验证：对已完成的 Todo 再次 complete，状态不变且不报错。
        幂等性是 REST API 设计的核心原则，这个用例说明你理解 API 设计。
        """
        todo = todo_api.create_todo(
            title="Idempotent Task", user_id=test_user["id"]
        )
        todo_api.complete_todo(todo["id"])
        updated = todo_api.complete_todo(todo["id"])
        assert updated["completed"] is True


class TestFilterTodos:

    def test_filter_by_user_id_returns_only_that_users_todos(
        self, todo_api: TodoApi, user_api: UserApi
    ) -> None:
        """
        过滤参数验证：GET /todos?user_id=X 只返回属于 X 的 Todo。
        验证查询参数过滤逻辑的正确性。
        """
        user_a = user_api.create_user(
            name="User A", email=f"a_{uuid.uuid4().hex[:6]}@test.com"
        )
        user_b = user_api.create_user(
            name="User B", email=f"b_{uuid.uuid4().hex[:6]}@test.com"
        )
        todo_api.create_todo(title="A's task", user_id=user_a["id"])
        todo_api.create_todo(title="B's task", user_id=user_b["id"])

        todos_of_a = todo_api.list_todos(user_id=user_a["id"])
        assert all(t["user_id"] == user_a["id"] for t in todos_of_a), \
            "过滤结果包含了其他用户的 Todo"


class TestDeleteTodo:

    def test_delete_todo_then_not_in_list(
        self, todo_api: TodoApi, test_user: dict
    ) -> None:
        todo = todo_api.create_todo(
            title="To be deleted", user_id=test_user["id"]
        )
        todo_api.delete_todo(todo["id"])
        all_todos = todo_api.list_todos()
        ids = [t["id"] for t in all_todos]
        assert todo["id"] not in ids
