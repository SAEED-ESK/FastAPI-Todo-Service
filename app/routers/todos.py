from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from app.models.todo import TodoModel
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from app.core.database import get_db

from enum import Enum

class SortField(str, Enum):
    id = "id"
    title = "title"
    is_completed = "is_completed"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

router = APIRouter()

@router.get("/", response_model=list[TodoResponse])
def get_todos(
    is_compeleted: bool | None = None,
    search: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=2, ge=1, le=20),
    sort_by: SortField = Query(default=SortField.id),
    sort_order: SortOrder = Query(default=SortOrder.asc),
    db: Session = Depends(get_db)
):
    statement = select(TodoModel)
    if is_compeleted is not None:
        statement = statement.where(
            TodoModel.is_completed == is_compeleted
        )
    if search:
        statement = statement.where(
            or_(
                TodoModel.title.contains(search),
                TodoModel.description.contains(search)
            )
        )

    sort_fields = {
        SortField.id: TodoModel.id,
        SortField.title: TodoModel.title,
        SortField.is_completed: TodoModel.is_completed
    }

    sort_column = sort_fields[sort_by]

    if sort_order == SortOrder.asc:
        statement = statement.order_by(sort_column.asc())
    else:
        statement = statement.order_by(sort_column.desc())

    statement = statement.offset(skip).limit(limit)
    todos = db.scalars(statement).all()
    return todos

@router.post("/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    new_todo = TodoModel(
        title=todo.title,
        description=todo.description
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo

# GET /todos/5
@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id:int, db: Session = Depends(get_db)):
    todo = db.scalar(select(TodoModel).where(TodoModel.id == todo_id))
    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found!"
        )
    
    return todo

@router.put("/{todo_id}", response_model=TodoResponse)
def edit_todo(
    todo_id:int,
    todo_data: TodoUpdate,
    db: Session = Depends(get_db)
):
    todo = db.scalar(select(TodoModel).where(TodoModel.id == todo_id))
    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found!"
        )

    update_data = todo_data.model_dump(
        exclude_unset=True
    )
    for field, value in update_data.items():
        setattr(todo, field, value)

    db.commit()
    db.refresh(todo)
    
    return todo

@router.delete("/{todo_id}")
def delete_todo(
    todo_id:int,
    db: Session = Depends(get_db)
):
    todo = db.scalar(select(TodoModel).where(TodoModel.id == todo_id))
    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found!"
        )

    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted successfully!"}

# GET /todos?completed=true
# @router.get("/")
# def root(completed: bool | None = None):
#     return {"Completed": completed}