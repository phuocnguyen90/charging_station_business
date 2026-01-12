from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class QuoteRequestBase(BaseModel):
    monthly_bill: float
    currency: str = "USD"
    location: Optional[str] = None
    roof_area: Optional[float] = None
    usage_profile_type: str = "standard"
    property_details: Dict[str, Any] = {}
    budget_preference: str = "Standard"
    interaction_source: str = "wizard"

class QuoteRequestCreate(QuoteRequestBase):
    raw_transcript: Optional[str] = None

class QuoteRequestOut(QuoteRequestBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
