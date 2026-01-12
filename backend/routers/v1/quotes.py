from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.quote import QuoteRequest, Quote
from models.user import User
from schemas.quote import QuoteRequestCreate, QuoteRequestOut
from routers.v1.auth import get_db, get_current_user

router = APIRouter()

@router.post("/requests", response_model=QuoteRequestOut)
def create_quote_request(
    request_in: QuoteRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save a user's quote request (Wizard inputs).
    User must be logged in.
    """
    quote_request = QuoteRequest(
        user_id=current_user.id,
        **request_in.dict()
    )
    db.add(quote_request)
    db.commit()
    db.refresh(quote_request)
    return quote_request

@router.get("/requests/my", response_model=List[QuoteRequestOut])
def read_my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    requests = db.query(QuoteRequest).filter(QuoteRequest.user_id == current_user.id).all()
    return requests
