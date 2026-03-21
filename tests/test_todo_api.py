import uuid
import pytest
from api.user_api import UserApi
from api.todo_api import TodoApi
from client.schema_validator import SchemaValidator, TODO_SCHEMA


@pytest.fixture(scope="module")
def test_user(user_api: UserApi):                # type: ignore[return]
    resp = user_api.create_user(
        name="Todo Owner",
        email=f"todo_owner_{uuid.uuid4().hex[:6]}@test.com",
    )
    user = resp.json()
    yield user
    user_api.delete_user(user["id"])


class TestCreateTodo:

    def test_create_returns_201_and_correct_fields(
        self, todo_api: TodoApi, test_user: dict
    ) -> None:
        resp = todo_api.create_todo(
            title="Buy milk", user_id=test_user["id"]
        )

        assert resp.status_code == 201
        body = resp.json()
        assert body["title"]     == "Buy milk"
        assert body["user_id"]   == test_user["id"]
        assert body["completed"] is False

    def test_create_for_nonexistent_user_returns_404(
        self, todo_api: TodoApi
    ) -> None:
        resp = todo_api.create_todo(title="Ghost", user_id=999999)

        assert resp.status_code == 404

    def test_response_schema_matches_definition(
        self, todo_api: TodoApi, test_user: dict
    ) -> None:
        resp = todo_api.create_todo(
            title="Schema Test", user_id=test_user["id"]
        )

        assert resp.status_code == 201
        SchemaValidator.assert_matches(resp.json(), TODO_SCHEMA)


class TestCompleteTodo:

    def test_complete_sets_flag_true(
        self, todo_api: TodoApi, test_user: dict
    ) -> None:
        create_resp = todo_api.create_todo(
            title="Task to complete", user_id=test_user["id"]
        )
        todo_id = create_resp.json()["id"]

        resp = todo_api.complete_todo(todo_id)

        assert resp.status_code == 200
        assert resp.json()["completed"] is True

    def test_complete_already_completed_is_idempotent(
        self, todo_api: TodoApi, test_user: dict
    ) -> None:
        create_resp = todo_api.create_todo(
            title="Idempotent Task", user_id=test_user["id"]
        )
        todo_id = create_resp.json()["id"]

        todo_api.complete_todo(todo_id)
        resp = todo_api.complete_todo(todo_id)

        assert resp.status_code == 200
        assert resp.json()["completed"] is True


class TestFilterTodos:

    def test_filter_by_user_id_returns_only_that_users_todos(
        self, todo_api: TodoApi, user_api: UserApi
    ) -> None:
        user_a = user_api.create_user(
            name="User A",
            email=f"a_{uuid.uuid4().hex[:6]}@test.com",
        ).json()
        user_b = user_api.create_user(
            name="User B",
            email=f"b_{uuid.uuid4().hex[:6]}@test.com",
        ).json()

        todo_api.create_todo(title="A task", user_id=user_a["id"])
        todo_api.create_todo(title="B task", user_id=user_b["id"])

        resp = todo_api.list_todos(user_id=user_a["id"])

        assert resp.status_code == 200
        todos = resp.json()
        assert all(t["user_id"] == user_a["id"] for t in todos)


class TestDeleteTodo:

    def test_delete_then_not_in_list(
        self, todo_api: TodoApi, test_user: dict
    ) -> None:
        create_resp = todo_api.create_todo(
            title="To be deleted", user_id=test_user["id"]
        )
        todo_id = create_resp.json()["id"]

        delete_resp = todo_api.delete_todo(todo_id)
        assert delete_resp.status_code == 204

        list_resp = todo_api.list_todos()
        all_ids = [t["id"] for t in list_resp.json()]
        assert todo_id not in all_ids
