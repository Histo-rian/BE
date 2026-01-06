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
    prompt = f"""
        당신은 사료 비판과 논리 분석에 정통한 전문 역사학자입니다. 
        다음 제공되는 글의 '역사적 사실 관계'와 '논술적 타당성'을 엄격하게 검증해 주세요. 

        분석은 다음 순서에 따라 한국어로 진행해 주세요:

        1. 요약: 작성자가 주장하는 핵심 요지는 무엇인가?
        2. 사실 검증: 글에 포함된 구체적인 역사적 사실(연도, 인물, 사건 등) 중 오류가 있는가?
        3. 논리 분석: 
        - 주장에 대한 근거가 적절한 사료(Primary/Secondary Sources)에 기반하고 있는가?
        - 인과관계 설정에 논리적 비약이나 오류(결과론적 해석, 확증 편향 등)가 없는가?
        4. 종합 판정: 이 글은 역사적 관점에서 '타당한 논리'인가, 아니면 '왜곡된 주장'인가?
        5. 보완 제언: 논리를 완성하기 위해 추가로 참고해야 할 사료나 관점은 무엇인가?

        [검증할 내용]:
        {post.contents}
    """
    
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
