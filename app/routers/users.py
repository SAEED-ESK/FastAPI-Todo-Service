from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.auth.jwt_auth import (
    generate_access_token,
    generate_refresh_token,
    get_authenticated_user,
    decode_refresh_token,
    decode_access_token
)
from app.schemas.user import (
    UserRefreshTokenSchema,
    UserRegisterSchema,
    UserloginSchema,
    LoginResponseSchema,
    UserChangePasswordSchema)
    
from app.core.database import get_db
from app.models.user import UserModel, RevokedToken
from app.messages.accounts import AccountMessages

router = APIRouter()

security = HTTPBearer()

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
            detail=AccountMessages.USER_ALREADY_EXISTS
        )

    # Password hashing
    user_obj = UserModel(username=request.username.lower())
    user_obj.set_password(request.password)
    db.add(user_obj)
    db.commit()

    return {"detail": AccountMessages.REGISTERED_SUCCESSFULLY}

@router.post(
        "/login",
        status_code=status.HTTP_200_OK,
        response_model=LoginResponseSchema
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
            detail=AccountMessages.INVALID_CREDENTIALS
        )

    if not user_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AccountMessages.USER_INACTIVE
        )

    access_token = generate_access_token(user_obj.id)
    refresh_token = generate_refresh_token(user_obj.id)
    
    return {
        "detail": AccountMessages.LOGGED_IN_SUCCESSFULLY,
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@router.get("/me")
def get_me(
    current_user: UserModel = Depends(get_authenticated_user),
):
    return {
        "id": current_user.id,
        "username": current_user.username
    }

@router.post("/change-password")
def change_password(
    request: UserChangePasswordSchema,
    current_user: UserModel = Depends(get_authenticated_user),
    db: Session = Depends(get_db)
):
    if not current_user.verify_password(request.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AccountMessages.INVALID_CREDENTIALS
        )
    if request.current_password == request.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=AccountMessages.NEW_PASSWORD_SAME_AS_OLD
        )
    
    current_user.set_password(request.new_password)
    db.commit()

    return {"detail": AccountMessages.CHANGE_PASSWORD_SUCCESSFULLY}

@router.post("/refresh-token")
def user_refresh_token(
    request: UserRefreshTokenSchema,
    db: Session = Depends(get_db)
):
    user_id = decode_refresh_token(request.token)
    access_token = generate_access_token(user_id)
    return {
            "access_token": access_token
        } 

@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    jti = payload["jti"]

    existing = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
    if existing:
        return {"detail": AccountMessages.LOGGED_OUT_SUCCESSFULLY}

    revoked_token = RevokedToken(
        jti=payload["jti"],
        expired_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    )
    db.add(revoked_token)
    db.commit()

    return {"detail": AccountMessages.LOGGED_OUT_SUCCESSFULLY}