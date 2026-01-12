from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import SessionLocal
from pydantic import BaseModel
import uuid
from typing import Dict, Any, Optional

router = APIRouter()

# In-memory store for shared links (Mocking database for now for speed)
# In production, this would be a DB table "SharedEstimate"
SHARED_ESTIMATES = {}

class SharedEstimateCreate(BaseModel):
    estimate_data: Dict[str, Any]
    expires_in_days: int = 7

class SharedEstimateOut(BaseModel):
    share_token: str
    url: str

@router.post("/share", response_model=SharedEstimateOut)
def create_shared_link(data: SharedEstimateCreate):
    token = str(uuid.uuid4())
    SHARED_ESTIMATES[token] = data.estimate_data
    return {
        "share_token": token,
        "url": f"/shared/{token}"
    }

@router.get("/share/{token}")
def get_shared_estimate(token: str):
    if token not in SHARED_ESTIMATES:
        raise HTTPException(status_code=404, detail="Estimate not found or expired")
    return SHARED_ESTIMATES[token]
