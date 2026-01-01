from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import SessionLocal
from app.crud.post import create_post as crud_create_post, get_all_posts, get_recent_posts, get_post, update_post, delete_post
from app.schemas.post import Post, PostCreate, PostUpdate

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Post)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    return crud_create_post(db=db, post=post)

@router.get("/", response_model=List[Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = get_all_posts(db, skip=skip, limit=limit)
    return posts

@router.get("/recent", response_model=List[Post])
def read_recent_posts(db: Session = Depends(get_db)):
    posts = get_recent_posts(db, limit=3)
    return posts

@router.get("/{post_id}", response_model=Post)
def read_post(post_id: int, db: Session = Depends(get_db)):
    db_post = get_post(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@router.put("/{post_id}", response_model=Post)
def update_existing_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    db_post = update_post(db, post_id=post_id, post_update=post)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@router.delete("/{post_id}", response_model=Post)
def delete_existing_post(post_id: int, db: Session = Depends(get_db)):
    db_post = delete_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post
