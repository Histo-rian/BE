import os
import json
from sqlalchemy.orm import Session
from app.models.models import User, Post
from app.schemas.post import PostCreate, PostUpdate
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
from google.genai import types

load_dotenv()

class VerificationResult(BaseModel):
    isReal: bool
    comment: str

# Vertex AI를 API 키 방식으로 호출하는 설정
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    vertexai=True, # 이 옵션이 핵심입니다!
    project="ecstatic-backup-483515-d3",
    location="us-central1"
)


def _verify_post_content(contents: str):
    prompt=f"""
        당신은 사료 비판과 역사적 개연성을 분석하는 전문 역사학자입니다. 
        제공된 글의 [역사적 사실성]과 [논리적 타당성]을 다음 기준에 따라 엄격히 검증하세요.

        1. 핵심 주장 요약: 작성자의 주된 논지를 한 문장으로 정리할 것.
        2. 사실 관계(Fact-Check): 언급된 연도, 인물, 사건 중 오류가 있다면 근거와 함께 교정할 것.
        3. 논리적 인과관계: 
        - 전제에서 결론으로 가는 과정에 논리적 비약이나 '결과론적 해석'이 없는가?
        - 특정 의도를 가지고 사료를 선택적으로 해석한 '확증 편향'이 보이는가?
        4. 학술적 타당성: 해당 주장이 역사학계의 통설과 일치하는지, 아니면 근거 있는 새로운 가설인지 판정할 것.
        5. 보완점: 논리의 완성도를 높이기 위해 추가로 검토해야 할 1차 사료나 연구 문헌을 제시할 것.

        [검증 대상 본문]:
        {contents[:2000]}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=VerificationResult,
            )
        )
        
        if response.parsed:
            return response.parsed.isReal, response.parsed.comment
        else:
            return False, "검증 결과를 얻을 수 없습니다."
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        if "429" in error_msg:
            return False, "AI 서버 과부하입니다. 잠시 후 다시 시도해주세요."
        return False, f"검증 중 오류 발생: {error_msg}"

def create_post(db: Session, post: PostCreate):
    user_exists = db.query(User).filter(User.id == post.author_id).first()
    if not user_exists:
        return {"error": "존재하지 않는 사용자 ID입니다."}
    
    verified_status, ai_comment = _verify_post_content(post.contents)
    
    db_post = Post(
        title=post.title,
        contents=post.contents,
        author_id=post.author_id,
        verified=verified_status
    )
    
    try:
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return {"post": db_post, "comment": ai_comment}
    except Exception as e:
        db.rollback()
        return {"error": "데이터 저장 중 오류가 발생했습니다."}

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
    
    ai_comment = None
    if "contents" in update_data:
        verified_status, ai_comment = _verify_post_content(update_data["contents"])
        db_post.verified = verified_status
    
    for key, value in update_data.items():
        setattr(db_post, key, value)
    
    db.commit()
    db.refresh(db_post)
    
    return {"post": db_post, "comment": ai_comment if ai_comment else "기존 검증 상태 유지"}

def delete_post(db: Session, post_id: int):
    db_post = get_post(db, post_id)
    if not db_post:
        return None
    
    db.delete(db_post)
    db.commit()
    return db_post
