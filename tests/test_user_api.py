import uuid
import pytest
from api.user_api import UserApi
from client.schema_validator import SchemaValidator, USER_SCHEMA


def unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


class TestListUsers:

    def test_list_returns_200_and_list_type(self, user_api: UserApi) -> None:
        resp = user_api.list_users()

        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)

    def test_list_after_create_contains_new_user(self, user_api: UserApi) -> None:
        email = unique_email()
        create_resp = user_api.create_user(name="List Test", email=email)
        created = create_resp.json()

        resp = user_api.list_users()
        body = resp.json()

        assert resp.status_code == 200
        ids = [u["id"] for u in body]
        assert created["id"] in ids


class TestCreateUser:

    def test_create_returns_201_and_correct_fields(self, user_api: UserApi) -> None:
        resp = user_api.create_user(name="Alice", email=unique_email())

        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Alice"
        assert body["role"] == "member"
        assert body["id"] > 0

    def test_create_with_admin_role(self, user_api: UserApi) -> None:
        resp = user_api.create_user(
            name="Admin User",
            email=unique_email(),
            role="admin",
        )

        assert resp.status_code == 201
        body = resp.json()
        assert body["role"] == "admin"

    def test_duplicate_email_returns_409(self, user_api: UserApi) -> None:
        email = unique_email()
        user_api.create_user(name="First", email=email)

        resp = user_api.create_user(name="Second", email=email)

        assert resp.status_code == 409

    def test_response_schema_matches_definition(self, user_api: UserApi) -> None:
        resp = user_api.create_user(name="Schema Test", email=unique_email())

        assert resp.status_code == 201
        SchemaValidator.assert_matches(resp.json(), USER_SCHEMA)

    @pytest.mark.parametrize("role", ["admin", "member", "guest"])
    def test_all_valid_roles_accepted(self, user_api: UserApi, role: str) -> None:
        resp = user_api.create_user(
            name=f"Role Test {role}",
            email=unique_email(),
            role=role,
        )

        assert resp.status_code == 201
        assert resp.json()["role"] == role


class TestGetUser:

    def test_get_existing_user_returns_200(
        self, user_api: UserApi, existing_user: dict
    ) -> None:
        resp = user_api.get_user(existing_user["id"])

        assert resp.status_code == 200
        body = resp.json()
        assert body["id"]    == existing_user["id"]
        assert body["email"] == existing_user["email"]

    def test_get_nonexistent_user_returns_404(self, user_api: UserApi) -> None:
        resp = user_api.get_user(user_id=999999)

        assert resp.status_code == 404


class TestUpdateUser:

    def test_update_name_reflects_in_response(
        self, user_api: UserApi, existing_user: dict
    ) -> None:
        resp = user_api.update_user(existing_user["id"], name="Updated Name")

        assert resp.status_code == 200
        body = resp.json()
        assert body["name"]  == "Updated Name"
        assert body["email"] == existing_user["email"]

    def test_update_role_to_guest(
        self, user_api: UserApi, existing_user: dict
    ) -> None:
        resp = user_api.update_user(existing_user["id"], role="guest")

        assert resp.status_code == 200
        assert resp.json()["role"] == "guest"


class TestDeleteUser:

    def test_delete_then_get_returns_404(self, user_api: UserApi) -> None:
        create_resp = user_api.create_user(
            name="To Delete", email=unique_email()
        )
        user_id = create_resp.json()["id"]

        delete_resp = user_api.delete_user(user_id)
        assert delete_resp.status_code == 204

        get_resp = user_api.get_user(user_id)
        assert get_resp.status_code == 404

    def test_delete_nonexistent_returns_404(self, user_api: UserApi) -> None:
        resp = user_api.delete_user(user_id=999999)

        assert resp.status_code == 404