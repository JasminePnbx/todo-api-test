import pytest
from api.user_api import UserApi
from utils.schema_validator import SchemaValidator, USER_SCHEMA
from client.response_assert import ResponseAssert
from utils.factories import UserPayloadFactory  # 🌟 引入数据工厂


class TestListUsers:

    def test_list_returns_200_and_list_type(self, user_api: UserApi) -> None:
        resp = user_api.list_users()

        body = ResponseAssert(resp).status(200).body()
        assert isinstance(body, list)

    def test_list_after_create_contains_new_user(self, user_api: UserApi) -> None:
        payload = UserPayloadFactory()
        create_resp = user_api.create_user(**payload)
        created = ResponseAssert(create_resp).status(201).body()

        resp = user_api.list_users()
        body = ResponseAssert(resp).status(200).body()

        ids = [u["id"] for u in body]
        assert created["id"] in ids


class TestCreateUser:

    def test_create_returns_201_and_correct_fields(self, user_api: UserApi) -> None:
        payload = UserPayloadFactory()
        resp = user_api.create_user(**payload)

        body = ResponseAssert(resp).status(201)\
            .field_equals("name", payload["name"])\
            .field_equals("email", payload["email"])\
            .field_equals("role", payload["role"])\
            .body()
        assert body["id"] > 0

    def test_create_with_admin_role(self, user_api: UserApi) -> None:
        payload = UserPayloadFactory(is_admin=True)
        resp = user_api.create_user(**payload)

        ResponseAssert(resp).status(201).field_equals("role", "admin")

    def test_duplicate_email_returns_409(self, user_api: UserApi) -> None:
        # 🌟 手动干预指定 email，制造冲突场景
        payload = UserPayloadFactory(email="conflict@test.com")
        user_api.create_user(**payload)

        resp = user_api.create_user(**payload)

        ResponseAssert(resp).status(409)

    def test_response_schema_matches_definition(self, user_api: UserApi) -> None:
        payload = UserPayloadFactory()
        resp = user_api.create_user(**payload)

        body = ResponseAssert(resp).status(201).body()
        SchemaValidator.assert_matches(body, USER_SCHEMA)

    @pytest.mark.parametrize("role", ["admin", "member", "guest"])
    def test_all_valid_roles_accepted(self, user_api: UserApi, role: str) -> None:
        # 🌟 结合参数化，动态注入 role
        payload = UserPayloadFactory(role=role)
        resp = user_api.create_user(**payload)

        ResponseAssert(resp).status(201).field_equals("role", role)


class TestGetUser:

    def test_get_existing_user_returns_200(
        self, user_api: UserApi, existing_user: dict
    ) -> None:
        resp = user_api.get_user(existing_user["id"])

        ResponseAssert(resp).status(200)\
            .field_equals("id", existing_user["id"])\
            .field_equals("email", existing_user["email"])

    def test_get_nonexistent_user_returns_404(self, user_api: UserApi) -> None:
        resp = user_api.get_user(user_id=999999)

        ResponseAssert(resp).status(404)


class TestUpdateUser:

    def test_update_name_reflects_in_response(
        self, user_api: UserApi, existing_user: dict
    ) -> None:
        resp = user_api.update_user(existing_user["id"], name="Updated Name")

        ResponseAssert(resp).status(200)\
            .field_equals("name", "Updated Name")\
            .field_equals("email", existing_user["email"])

    def test_update_role_to_guest(
        self, user_api: UserApi, existing_user: dict
    ) -> None:
        resp = user_api.update_user(existing_user["id"], role="guest")

        ResponseAssert(resp).status(200).field_equals("role", "guest")


class TestDeleteUser:

    def test_delete_then_get_returns_404(self, user_api: UserApi) -> None:
        payload = UserPayloadFactory()
        create_resp = user_api.create_user(**payload)
        user_id = ResponseAssert(create_resp).status(201).body()["id"]

        delete_resp = user_api.delete_user(user_id)
        ResponseAssert(delete_resp).status(204)

        get_resp = user_api.get_user(user_id)
        ResponseAssert(get_resp).status(404)

    def test_delete_nonexistent_returns_404(self, user_api: UserApi) -> None:
        resp = user_api.delete_user(user_id=999999)

        ResponseAssert(resp).status(404)