from fastapi import (
    HTTPException, Depends, status)
from fastapi.security import (
    HTTPBearer, HTTPAuthorizationCredentials)
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.core.config import settings
from app.models.user import UserModel
from app.messages.accounts import AccountMessages

import jwt

security = HTTPBearer()

def get_authenticated_user(
     credentials: HTTPAuthorizationCredentials = Depends(security),
     db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        decoded = jwt.decode(
            token,
            settings.AUTH_JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = decoded.get("user_id", None)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountMessages.USER_ID_NOT_IN_TOKEN
            )
        if decoded.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountMessages.INVALID_TOKEN_TYPE
            )
        user_obj = db.query(UserModel).filter_by(id=user_id).one_or_none()
        if not user_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountMessages.USER_NOT_FOUND
            )
        return user_obj
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AccountMessages.INVALID_TOKEN
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AccountMessages.INVALID_TOKEN
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AccountMessages.TOKEN_EXPIRED
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AccountMessages.INVALID_TOKEN
        )


def generate_access_token(user_id: int, expires_in: int = 3600) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
        "user_id": user_id
    }
    return jwt.encode(payload, settings.AUTH_JWT_SECRET_KEY, algorithm="HS256")

def generate_refresh_token(user_id: int, expires_in: int = 3600*24) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
        "user_id": user_id
    }
    return jwt.encode(payload, settings.AUTH_JWT_SECRET_KEY, algorithm="HS256")

def decode_refresh_token(token):
    try:
        decoded = jwt.decode(
            token,
            settings.AUTH_JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = decoded.get("user_id", None)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountMessages.USER_ID_NOT_IN_TOKEN
            )
        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AccountMessages.INVALID_TOKEN_TYPE
            )
        return user_id

    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AccountMessages.INVALID_TOKEN
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AccountMessages.INVALID_TOKEN
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AccountMessages.TOKEN_EXPIRED
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AccountMessages.INVALID_TOKEN
        )