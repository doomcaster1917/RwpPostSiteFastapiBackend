import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy_utils import PasswordType
from .database import Base

intpk = Annotated[int, mapped_column(primary_key=True, index=True)]
created_at_type = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    nickname: Mapped[str] = mapped_column(unique=True)
    avatar_path: Mapped[str] = mapped_column(nullable=True)
    is_admin: Mapped[bool] = mapped_column(nullable=True)
    is_locked: Mapped[bool] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(PasswordType(schemes=['pbkdf2_sha512', 'md5_crypt'], deprecated=['md5_crypt']))
    date_registration: Mapped[created_at_type]
    refresh_token: Mapped[str] = mapped_column(nullable=True)
    post_comments = relationship("Comment", back_populates="user")

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[intpk]
    text: Mapped[str] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    date_made: Mapped[created_at_type]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete='CASCADE'))
    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="post_comments")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[intpk]
    title: Mapped[str]
    text: Mapped[str]
    date_made: Mapped[created_at_type]
    img_path: Mapped[str]

    comments = relationship("Comment", back_populates="post")


