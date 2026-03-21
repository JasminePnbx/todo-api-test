# tests/db_helper.py
"""
数据库验证工具。
测试用例通过这个模块直接查 SQLite，
验证接口操作真实写入了数据库，而不只是 HTTP 响应正确。
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test_app.db"

engine  = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)


def get_user_from_db(user_id: int) -> dict | None:
    """直接查数据库，返回用户记录；不存在返回 None。"""
    with Session() as db:
        row = db.execute(
            text("SELECT id, name, email, role FROM users WHERE id = :id"),
            {"id": user_id}
        ).fetchone()
        if row is None:
            return None
        return {"id": row.id, "name": row.name,
                "email": row.email, "role": row.role}


def get_todo_from_db(todo_id: int) -> dict | None:
    """直接查数据库，返回 Todo 记录；不存在返回 None。"""
    with Session() as db:
        row = db.execute(
            text("SELECT id, title, user_id, completed FROM todos WHERE id = :id"),
            {"id": todo_id}
        ).fetchone()
        if row is None:
            return None
        return {"id": row.id, "title": row.title,
                "user_id": row.user_id, "completed": bool(row.completed)}


def user_exists_in_db(user_id: int) -> bool:
    """检查用户在数据库里是否存在。"""
    return get_user_from_db(user_id) is not None


def count_users_in_db() -> int:
    """返回数据库里当前的用户总数。"""
    with Session() as db:
        result = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()
        return result[0]