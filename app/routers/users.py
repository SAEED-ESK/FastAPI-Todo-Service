from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..schemas.user import UserRegisterSchema
from ..core.database import get_db
from ..models.user import UserModel

router = APIRouter()

@router.post(
        "/register",
        status_code=status.HTTP_201_CREATED
    )
def register(
    request: UserRegisterSchema,
    db: Session = Depends(get_db)
):
    # Checking if user already exists
    if (
        db.query(UserModel).filter_by(
            username=request.username.lower()
        ).first()
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists!"
        )

    # Password hashing
    user_obj = UserModel(username=request.username.lower())
    user_obj.set_password(request.password)
    db.add(user_obj)
    db.commit()

    return {"detail": "user registered successfully"}