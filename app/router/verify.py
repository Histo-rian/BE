from fastapi import APIRouter, HTTPException
from app.schemas.verify import VerifyRequest, VerifyResponse
from app.core.gemini import verify_historical_fact

router = APIRouter(
    prefix="/verify",
    tags=["verify"]
)

@router.post("", response_model=VerifyResponse)
async def verify_fact(request: VerifyRequest):
    try:
        result = verify_historical_fact(request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
