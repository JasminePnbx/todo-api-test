import sys
import os
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 🌟 核心修复 1：动态补全路径，确保能找到根目录的 config.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from config import settings

# 🌟 核心修复 2：使用配置中心的地址
SQLALCHEMY_DATABASE_URL = settings.db_url

# 数据库引擎与会话初始化
# 如果是 SQLite 加上特殊参数，MySQL 不需要
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── 数据模型（对应数据库表） ──────────────────────────────────
class UserModel(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name     = Column(String(255),  nullable=False)
    email    = Column(String(255),  unique=True, nullable=False, index=True)
    role     = Column(String(50),   default="member")

class TodoModel(Base):
    __tablename__ = "todos"
    id        = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title     = Column(String(255),  nullable=False)
    user_id   = Column(Integer, nullable=False)
    completed = Column(Boolean, default=False)

# 🌟 核心修复 3：启动时强制自动建表（解决 Table doesn't exist）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Pydantic 模式（用于接口校验） ─────────────────────────────
class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "member"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class TodoCreate(BaseModel):
    title: str
    user_id: int

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None

# ── 接口路由 ──────────────────────────────────────────────────

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users]

@app.post("/users", status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserModel).filter(UserModel.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    user = UserModel(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}

@app.put("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, val in payload.model_dump().items():
        if val is not None:
            setattr(user, key, val)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()

@app.get("/todos")
def list_todos(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(TodoModel)
    if user_id:
        query = query.filter(TodoModel.user_id == user_id)
    todos = query.all()
    return [{"id": t.id, "title": t.title, "user_id": t.user_id, "completed": t.completed} for t in todos]

@app.post("/todos", status_code=201)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    # 验证用户是否存在
    if not db.query(UserModel).filter(UserModel.id == payload.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    todo = TodoModel(**payload.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return {"id": todo.id, "title": todo.title, "user_id": todo.user_id, "completed": todo.completed}

@app.patch("/todos/{todo_id}")
def update_todo(todo_id: int, payload: TodoUpdate, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, val in payload.model_dump().items():
        if val is not None:
            setattr(todo, key, val)
    db.commit()
    db.refresh(todo)
    return {"id": todo.id, "title": todo.title, "user_id": todo.user_id, "completed": todo.completed}

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()