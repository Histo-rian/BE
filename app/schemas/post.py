from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    title: str
    contents: str
    author_id: int
    verified: bool

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    contents: Optional[str] = None

class Post(PostBase):
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PostWithComment(BaseModel):
    post: Post
    comment: str