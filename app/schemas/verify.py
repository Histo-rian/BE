from pydantic import BaseModel

class VerifyRequest(BaseModel):
    message: str

class VerifyResponse(BaseModel):
    comment: str
    isReal: bool
