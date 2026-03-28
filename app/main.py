from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

app = FastAPI(title="User Todo API", version="2.0.0")

# 🌟 已经改好：直接连接你的 Docker MySQL
DATABASE_URL = "mysql+pymysql://root:123456@127.0.0.1:3306/todo_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# ── 数据模型（对应数据库表） ──────────────────────────────────
class UserModel(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name     = Column(String(255),  nullable=False)  # 🌟 修复：加上了长度 255
    email    = Column(String(255),  unique=True, nullable=False, index=True) # 🌟 修复
    role     = Column(String(50),   default="member") # 🌟 修复

class TodoModel(Base):
    __tablename__ = "todos"
    id        = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title     = Column(String(255),  nullable=False) # 🌟 修复
    user_id   = Column(Integer, nullable=False)
    completed = Column(Boolean, default=False)

# 启动时自动建表
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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