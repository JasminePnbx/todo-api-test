from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="User Todo API", version="1.0.0")

# ── 内存存储，模拟数据库 ──────────────────────────────────────
_users: dict[int, dict] = {}
_todos: dict[int, dict] = {}
_user_id_seq = 1
_todo_id_seq = 1


# ── 请求体模型 ────────────────────────────────────────────────
class UserCreate(BaseModel):
    name:  str
    email: str
    role:  str = "member"

class UserUpdate(BaseModel):
    name:  Optional[str] = None
    email: Optional[str] = None
    role:  Optional[str] = None

class TodoCreate(BaseModel):
    title:   str
    user_id: int

class TodoUpdate(BaseModel):
    title:     Optional[str]  = None
    completed: Optional[bool] = None


# ── User 接口 ─────────────────────────────────────────────────
@app.get("/users", summary="获取所有用户")
def list_users():
    return list(_users.values())

@app.post("/users", status_code=201, summary="创建用户")
def create_user(payload: UserCreate):
    global _user_id_seq
    if any(u["email"] == payload.email for u in _users.values()):
        raise HTTPException(status_code=409, detail="Email already exists")
    user = {"id": _user_id_seq, **payload.model_dump()}
    _users[_user_id_seq] = user
    _user_id_seq += 1
    return user

@app.get("/users/{user_id}", summary="获取单个用户")
def get_user(user_id: int):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    return _users[user_id]

@app.put("/users/{user_id}", summary="更新用户")
def update_user(user_id: int, payload: UserUpdate):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    _users[user_id].update(updates)
    return _users[user_id]

@app.delete("/users/{user_id}", status_code=204, summary="删除用户")
def delete_user(user_id: int):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    del _users[user_id]


# ── Todo 接口 ─────────────────────────────────────────────────
@app.get("/todos", summary="获取所有 Todo")
def list_todos(user_id: Optional[int] = None):
    todos = list(_todos.values())
    if user_id is not None:
        todos = [t for t in todos if t["user_id"] == user_id]
    return todos

@app.post("/todos", status_code=201, summary="创建 Todo")
def create_todo(payload: TodoCreate):
    global _todo_id_seq
    if payload.user_id not in _users:
        raise HTTPException(status_code=404, detail="User not found")
    todo = {"id": _todo_id_seq, "completed": False, **payload.model_dump()}
    _todos[_todo_id_seq] = todo
    _todo_id_seq += 1
    return todo

@app.patch("/todos/{todo_id}", summary="更新 Todo 状态")
def update_todo(todo_id: int, payload: TodoUpdate):
    if todo_id not in _todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    _todos[todo_id].update(updates)
    return _todos[todo_id]

@app.delete("/todos/{todo_id}", status_code=204, summary="删除 Todo")
def delete_todo(todo_id: int):
    if todo_id not in _todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    del _todos[todo_id]