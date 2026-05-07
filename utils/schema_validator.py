import logging
from typing import Any
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)

USER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["id", "name", "email", "role"],
    "properties": {
        "id":    {"type": "integer", "minimum": 1},
        "name":  {"type": "string",  "minLength": 1},
        "email": {"type": "string",  "minLength": 1},
        "role":  {"type": "string",
                  "enum": ["admin", "member", "guest"]},
    },
    "additionalProperties": False,
}

TODO_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["id", "title", "user_id", "completed"],
    "properties": {
        "id":        {"type": "integer", "minimum": 1},
        "title":     {"type": "string",  "minLength": 1},
        "user_id":   {"type": "integer", "minimum": 1},
        "completed": {"type": "boolean"},
    },
    "additionalProperties": False,
}


class SchemaValidator:
    @staticmethod
    def assert_matches(body: Any, schema: dict[str, Any]) -> None:
        try:
            validate(instance=body, schema=schema)
            logger.debug("Schema OK")
        except ValidationError as exc:
            logger.error("Schema FAIL | path=%s | reason=%s",
                         exc.json_path, exc.message)
            raise AssertionError(
                f"Schema 断言失败\n"
                f"  路径: {exc.json_path}\n"
                f"  原因: {exc.message}\n"
                f"  实际: {exc.instance!r}"
            ) from exc
