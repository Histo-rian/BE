from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

follows = Table(
    "follows",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("following_id", Integer, ForeignKey("users.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    posts = relationship("Post", back_populates="author")
    
    following = relationship(
        "User",
        secondary=follows,
        primaryjoin=(id == follows.c.follower_id),
        secondaryjoin=(id == follows.c.following_id),
        backref="followers"
    )

class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    contents = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified = Column(Boolean, default=False)

    author = relationship("User", back_populates="posts")
