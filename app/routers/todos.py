from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "All todos"}

@router.post("/")
def root():
    return {"message": "Create todos"}

# GET /todos/5
@router.get("/{todo_id}")
def root(todo_id:int):
    return {"todo id": todo_id}

# GET /todos?completed=true
@router.get("/")
def root(completed: bool | None = None):
    return {"Completed": completed}