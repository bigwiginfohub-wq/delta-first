from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mode 3 passphrase hash (DeltaFirst2026)
CORRECT_HASH = "6c4be6fabdafd60bd766b15b572d67f26006e52723a58f521900cb47234aed7d"

class VerifyRequest(BaseModel):
    passphrase: str

@app.get("/")
def root():
    return {"message": "Delta-First Mode 3 API is running"}

@app.post("/verify")
def verify(request: VerifyRequest):
    input_hash = hashlib.sha256(request.passphrase.encode()).hexdigest()
    if input_hash != CORRECT_HASH:
        raise HTTPException(status_code=401, detail="ACCESS DENIED")
    return {"status": "VERIFIED", "message": "Access granted"}