from fastapi import FastAPI
from app.routers import todos, users
from app.core.database import Base, engine
from app.models.todo import TodoModel

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(
    todos.router,
    prefix="/todos",
    tags=["Todos"]
    )
app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
    )