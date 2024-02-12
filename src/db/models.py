from sqlalchemy import SmallInteger, BigInteger
from sqlalchemy.orm import mapped_column
from .base import Base


class Users(Base):
    __tablename__ = "users"

    id = mapped_column(BigInteger, primary_key=True)
    status = mapped_column(SmallInteger, default=0)
    interlocutor = mapped_column(BigInteger, nullable=True)