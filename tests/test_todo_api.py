# tests/test_todo_api.py
import pytest
from client.response_assert import ResponseAssert
from utils.factories import TodoPayloadFactory, UserPayloadFactory

class TestTodoAPI:
    @pytest.fixture(scope="class")
    def test_user(self, user_api):
        """创建一个测试用户供 todo 使用"""
        payload = UserPayloadFactory()
        resp = user_api.create_user(**payload)
        user = ResponseAssert(resp).status(201).body()
        yield user
        user_api.delete_user(user["id"])

    def test_create_todo(self, todo_api, test_user):
        payload = TodoPayloadFactory(user_id=test_user["id"])
        resp = todo_api.create_todo(**payload)
        ResponseAssert(resp).status(201)\
            .field_equals("title", payload["title"])\
            .field_equals("user_id", test_user["id"])\
            .field_equals("completed", False)

    def test_list_todos(self, todo_api, test_user):
        # 先创建一条 todo
        payload = TodoPayloadFactory(user_id=test_user["id"])
        create_resp = todo_api.create_todo(**payload)
        todo_id = ResponseAssert(create_resp).status(201).body()["id"]

        # 列出所有 todos
        resp = todo_api.list_todos()
        ResponseAssert(resp).status(200)
        body = resp.json()
        assert isinstance(body, list)
        assert any(t["id"] == todo_id for t in body)

    def test_list_todos_filter_by_user(self, todo_api, test_user):
        resp = todo_api.list_todos(user_id=test_user["id"])
        ResponseAssert(resp).status(200)
        body = resp.json()
        for todo in body:
            assert todo["user_id"] == test_user["id"]

    def test_complete_todo(self, todo_api, test_user):
        payload = TodoPayloadFactory(user_id=test_user["id"], completed=False)
        create_resp = todo_api.create_todo(**payload)
        todo_id = ResponseAssert(create_resp).status(201).body()["id"]

        resp = todo_api.complete_todo(todo_id)
        ResponseAssert(resp).status(200).field_equals("completed", True)

    def test_delete_todo(self, todo_api, test_user):
        payload = TodoPayloadFactory(user_id=test_user["id"])
        create_resp = todo_api.create_todo(**payload)
        todo_id = ResponseAssert(create_resp).status(201).body()["id"]

        del_resp = todo_api.delete_todo(todo_id)
        ResponseAssert(del_resp).status(204)

        # 验证已删除
        get_resp = todo_api.list_todos()
        body = get_resp.json()
        assert not any(t["id"] == todo_id for t in body)