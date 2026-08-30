from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.jwt_auth import (
    generate_access_token,
    generate_refresh_token,
    get_authenticated_user,
    decode_refresh_token
)
from ..schemas.user import (
    UserRefreshTokenSchema,
    UserRegisterSchema,
    UserloginSchema)
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

@router.post(
        "/login",
        status_code=status.HTTP_200_OK
    )
def login(
    request: UserloginSchema,
    db: Session = Depends(get_db)
):
    # Checking if user already exists

    user_obj = db.query(UserModel).filter_by(
        username=request.username.lower()
    ).first()

    if not user_obj or not user_obj.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password is incorrect!"
        )

    access_token = generate_access_token(user_obj.id)
    refresh_token = generate_refresh_token(user_obj.id)
    
    return {
        "detail": "user login successfully",
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@router.get("/me")
def get_me(
    current_user: UserModel = Depends(get_authenticated_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username
    }

@router.post("/refresh-token")
def user_refresh_token(
    request: UserRefreshTokenSchema,
    db: Session = Depends(get_db)
):
    user_id = decode_refresh_token(request.token)
    access_token = generate_access_token(user_id)
    return {
            "detail": "user access token successfully generate",
            "access_token": access_token
        } 