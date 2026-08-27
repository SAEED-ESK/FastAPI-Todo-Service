from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from passlib.context import CryptContext

from ..core.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordMixin:
    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password)

    def set_password(self, plain_text: str) -> None:
        print(type(plain_text))
        print(len(plain_text))
        self.hashed_password = pwd_context.hash(plain_text)

class UserModel(Base, PasswordMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(250), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    todos: Mapped[list["TodoModel"]]=relationship(
        back_populates="user"
    )
