from sqlalchemy.orm import Session
from app.models.models import Post
from app.schemas.post import PostCreate, PostUpdate
import time
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class VerificationResult(BaseModel):
    isReal: bool
    comment: str

def create_post(db: Session, post: PostCreate):
    prompt = f"당신은 전문 역사학자입니다. 다음 내용의 역사적 사실 여부를 판단하고 반드시 한국어로 설명해주세요: {post.contents}"
    
    time.sleep(1) 
            
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': VerificationResult,
        }
    )
    
    if response.parsed:
        result = response.parsed
    else:
        raw_data = json.loads(response.text)
        result = VerificationResult(**raw_data)
    
    db_post = Post(
        title=post.title,
        contents=post.contents,
        author_id=post.author_id,
        verified=result.isReal
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {"post": db_post, "comment": result.comment}

def get_all_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Post).offset(skip).limit(limit).all()

def get_recent_posts(db: Session, limit: int = 3):
    return db.query(Post).order_by(Post.created_at.desc()).limit(limit).all()

def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.post_id == post_id).first()

def get_post_by_title(db: Session, post_title: str):
    return db.query(Post).filter(Post.title.contains(post_title)).all()

def get_user_post(db: Session, user_id: int):
    return db.query(Post).filter(Post.author_id == user_id).all()

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
