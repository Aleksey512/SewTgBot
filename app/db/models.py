from datetime import datetime
from typing import List

import bcrypt
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Table, Numeric
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db.conn import Base

brigade_object = Table(
    "brigade_object", Base.metadata,
    Column("brigade_id", Integer(), ForeignKey("brigades_table.id", ondelete="CASCADE"), primary_key=True, unique=True),
    Column("object_id", Integer(), ForeignKey("objects_table.id", ondelete="CASCADE"), primary_key=True)
)


class User_Procedure(Base):
    __tablename__ = "user_procedure"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users_table.id"))
    procedure_id: Mapped[int] = mapped_column(ForeignKey("procedures_table.id"))
    count: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(Date, onupdate=datetime.now(), default=datetime.now())
    user: Mapped["User"] = relationship(back_populates="procedures")
    procedure: Mapped["Procedure"] = relationship(back_populates="users")


class Brigade(Base):
    __tablename__ = "brigades_table"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(32), nullable=True)
    number: Mapped[int] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(Date, onupdate=datetime.now(), default=datetime.now())
    user: Mapped[List["User"]] = relationship()
    objects: Mapped["Object"] = relationship(
        secondary=brigade_object, back_populates="brigades"
    )


class User(Base):
    __tablename__ = "users_table"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    brigade_id: Mapped["Brigade"] = mapped_column(ForeignKey("brigades_table.id", ondelete="SET NULL"), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(64), nullable=True)
    surname: Mapped[str] = mapped_column(String(64), nullable=True)
    telegram_id: Mapped[str] = mapped_column(String, index=True, nullable=True, unique=True)
    login: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    password: Mapped[bytes] = mapped_column(BYTEA)
    role: Mapped[str] = mapped_column(String(32), default="employee")
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(Date, onupdate=datetime.now(), default=datetime.now())

    procedures: Mapped[List["User_Procedure"]] = relationship(back_populates="user")

    def set_password(self, password: str) -> None:
        byte_password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(byte_password, salt)

    def check_password(self, password: str) -> bool:
        byte_password = password.encode('utf-8')
        return bcrypt.checkpw(byte_password, self.password)


class Object(Base):
    __tablename__ = "objects_table"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(Date, onupdate=datetime.now(), default=datetime.now())
    procedures: Mapped[List["Procedure"]] = relationship()
    brigades: Mapped[List["Brigade"]] = relationship(
        secondary=brigade_object, back_populates="objects"
    )


class Procedure(Base):
    __tablename__ = "procedures_table"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    object_id: Mapped["Object"] = mapped_column(ForeignKey('objects_table.id', ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    time: Mapped[int] = mapped_column()
    tariff: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    rate: Mapped[float] = mapped_column(Numeric(precision=10, scale=2))
    created_at: Mapped[datetime] = mapped_column(Date, default=datetime.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(Date, onupdate=datetime.now(), default=datetime.now())
    users: Mapped[List["User_Procedure"]] = relationship(back_populates="procedure")
