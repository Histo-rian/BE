import os
import time
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class VerificationResult(BaseModel):
    isReal: bool
    comment: str

def verify_historical_fact(text: str, max_retries=5):
    prompt = f"당신은 전문 역사학자입니다. 다음 내용의 역사적 사실 여부를 판단하고 반드시 한국어로 설명해주세요: {text}"
    
    delay = 2 
    
    for attempt in range(max_retries):
        try:
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
                return response.parsed
            return json.loads(response.text)

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"[시도 {attempt+1}] 제한 발생. {delay}초 후 재시도합니다...")
                time.sleep(delay)
                delay *= 2
            else:
                print(f"에러: {error_msg}")
                break
                
    return {"isReal": False, "comment": "지속적인 요청 제한으로 인해 처리에 실패했습니다."}
