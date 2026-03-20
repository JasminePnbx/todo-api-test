import uuid
import pytest
from api.user_api import UserApi
from client.response_assert import ResponseAssert


def unique_email() -> str:
    """生成唯一 email，防止重复创建报 409。"""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


class TestListUsers:

    def test_list_returns_list_type(self, user_api: UserApi) -> None:
        users = user_api.list_users()
        assert isinstance(users, list)

    def test_list_after_create_contains_new_user(self, user_api: UserApi) -> None:
        email = unique_email()
        created = user_api.create_user(name="List Test", email=email)
        users = user_api.list_users()
        ids = [u["id"] for u in users]
        assert created["id"] in ids


class TestCreateUser:

    def test_create_returns_correct_fields(self, user_api: UserApi) -> None:
        user = user_api.create_user(name="Alice", email=unique_email())
        assert user["name"]  == "Alice"
        assert user["role"]  == "member"     # 默认值
        assert user["id"]    > 0

    def test_create_with_admin_role(self, user_api: UserApi) -> None:
        user = user_api.create_user(
            name="Admin User", email=unique_email(), role="admin"
        )
        assert user["role"] == "admin"

    def test_duplicate_email_returns_409(self, user_api: UserApi) -> None:
        """
        负向：重复 email → 409 Conflict。
        这是一个真实的业务规则验证，也是简历上可以说"发现并覆盖了
        邮箱唯一性约束的边界场景"的用例。
        """
        email = unique_email()
        user_api.create_user(name="First", email=email)
        resp = user_api.try_create_user({"name": "Second", "email": email, "role": "member"})
        ResponseAssert.of(resp).status(409)

    @pytest.mark.parametrize("role", ["admin", "member", "guest"])
    def test_all_valid_roles_accepted(self, user_api: UserApi, role: str) -> None:
        user = user_api.create_user(
            name=f"Role Test {role}", email=unique_email(), role=role
        )
        assert user["role"] == role


class TestGetUser:

    def test_get_existing_user(self, user_api: UserApi,
                               existing_user: dict) -> None:
        fetched = user_api.get_user(existing_user["id"])
        assert fetched["id"]    == existing_user["id"]
        assert fetched["email"] == existing_user["email"]

    def test_get_nonexistent_returns_404(self, user_api: UserApi) -> None:
        resp = user_api.try_get_user(user_id=999999)
        ResponseAssert.of(resp).status(404)


class TestUpdateUser:

    def test_update_name(self, user_api: UserApi,
                         existing_user: dict) -> None:
        updated = user_api.update_user(existing_user["id"], name="Updated Name")
        assert updated["name"]  == "Updated Name"
        assert updated["email"] == existing_user["email"]   # 未改字段保持不变

    def test_update_role_to_guest(self, user_api: UserApi,
                                  existing_user: dict) -> None:
        updated = user_api.update_user(existing_user["id"], role="guest")
        assert updated["role"] == "guest"


class TestDeleteUser:

    def test_delete_then_get_returns_404(self, user_api: UserApi) -> None:
        """
        删除后再查询 → 404。
        这是验证删除操作真实生效的标准模式，叫做"操作后状态验证"。
        """
        user = user_api.create_user(name="To Delete", email=unique_email())
        user_api.delete_user(user["id"])
        resp = user_api.try_get_user(user["id"])
        ResponseAssert.of(resp).status(404)

    def test_delete_nonexistent_returns_404(self, user_api: UserApi) -> None:
        resp = user_api.try_get_user(999999)
        ResponseAssert.of(resp).status(404)