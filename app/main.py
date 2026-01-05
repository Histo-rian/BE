from fastapi import FastAPI
from app.core.database import engine
from app.router.post import router as post_router
from app.router.auth import router as auth_router
from app.router.verify import router as verify_router
from app.models.models import Base
from app.models import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

origins= [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post_router)
app.include_router(auth_router)
app.include_router(verify_router)

@app.get("/")
def root():
    return {"message": "Hello World"}