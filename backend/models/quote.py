from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, JSON, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class QuoteRequest(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True) 
    
    # Core User Needs
    monthly_bill = Column(Float, nullable=True) # Allow null if they only know "approximate"
    currency = Column(String, default="USD")
    
    # Advanced / Inferred Details
    location = Column(String, nullable=True) # Address or Lat/Long string
    roof_area = Column(Float, nullable=True)
    
    # Profiling (Defaults provided by Wizard/LLM)
    usage_profile_type = Column(String, default="standard") # standard, working_9_5, stay_at_home, night_owl
    property_details = Column(JSON, default={}) # { "roof_type": "tile", "shading": "partial", "azimuth": 180 }
    
    # Budget
    budget_preference = Column(String, default="Standard") 
    
    # Source / Context
    interaction_source = Column(String, default="wizard") # wizard, chat_llm
    raw_transcript = Column(Text, nullable=True) # For LLM extracted requests
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Quote(Base):
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("quoterequest.id"), nullable=False)
    installer_id = Column(Integer, ForeignKey("user.id"), nullable=False) 
    
    # JSON blob of selected InventoryListings
    system_configuration = Column(JSON, nullable=False)
    
    total_price = Column(Float, nullable=False)
    estimated_roi_years = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_accepted = Column(Boolean, default=False)
    
    request = relationship("QuoteRequest", backref="quotes")
    installer = relationship("User", backref="generated_quotes")
