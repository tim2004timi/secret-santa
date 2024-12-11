from sqlalchemy import DateTime, Table, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from datetime import datetime

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    tg_username: Mapped[str] = mapped_column(unique=True, nullable=False)

    # Внешний ключ, ссылающийся на id другого пользователя
    gift_to_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    # Связь с другим пользователем (кому дарит подарок)
    gift_to: Mapped["User"] = relationship(
        "User",
        remote_side=[id],
        back_populates="gift_from",
        foreign_keys=[gift_to_id],
        uselist=False,
    )

    # Обратная связь: список пользователей, которые дарят подарок этому пользователю
    gift_from: Mapped[list["User"]] = relationship(
        "User", back_populates="gift_to", foreign_keys=[gift_to_id]
    )

    hero_id: Mapped[int | None] = mapped_column(ForeignKey("heroes.id"), nullable=True)
    hero: Mapped["Hero"] = relationship(back_populates="user")

    def __repr__(self):
        return self.name


class Hero(Base):
    __tablename__ = "heroes"

    name: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="hero")
