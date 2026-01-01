from sqlalchemy.orm import Session
from app.models.models import Post
from app.schemas.post import PostCreate, PostUpdate

def create_post(db: Session, post: PostCreate):
    db_post = Post(
        title=post.title,
        contents=post.contents,
        author_id=post.author_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_all_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Post).offset(skip).limit(limit).all()

def get_recent_posts(db: Session, limit: int = 3):
    return db.query(Post).order_by(Post.created_at.desc()).limit(limit).all()

def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.post_id == post_id).first()

def update_post(db: Session, post_id: int, post_update: PostUpdate):
    db_post = get_post(db, post_id)
    if not db_post:
        return None
    
    update_data = post_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_post, key, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, post_id: int):
    db_post = get_post(db, post_id)
    if not db_post:
        return None
    
    db.delete(db_post)
    db.commit()
    return db_post
