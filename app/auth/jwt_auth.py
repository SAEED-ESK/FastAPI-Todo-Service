from fastapi import (
    Request, HTTPException, Depends, status)
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.core.config import settings
from app.models.user import UserModel
import jwt

def get_authenticated_user(
     request: Request,
     db: Session = Depends(get_db)
):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    try:
        decoded = jwt.decode(
            access_token,
            settings.AUTH_JWT_SECRET_KEY,
            algorithms="HS256"
        )
        user_id = decoded.get("user_id", None)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed! user_id is not in token"
            )
        if decoded.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed! token type is invalid"
            )
        if datetime.now() > datetime.fromtimestamp(decoded.get("exp")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed! token expired"
            )
        user_obj = db.query(UserModel).filter_by(id=user_id).one_or_none()
        return user_obj
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, invalid signature",
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, decode failed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed, {e}",
        )


def generate_access_token(user_id: int, expires_in: int = 300) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
        "user_id": user_id
    }
    return jwt.encode(payload, settings.AUTH_JWT_SECRET_KEY, algorithms="HS256")

def generate_refresh_token(user_id: int, expires_in: int = 3600*24) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
        "user_id": user_id
    }
    return jwt.encode(payload, settings.AUTH_JWT_SECRET_KEY, algorithms="HS256")