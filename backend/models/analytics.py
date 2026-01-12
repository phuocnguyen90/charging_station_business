from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base
import enum

class EventType(str, enum.Enum):
    LOGIN = "login"
    VIEW_PRODUCT = "view_product" 
    RUN_SIMULATION = "run_simulation"
    FILTER_INVENTORY = "filter_inventory"
    VIEW_QUOTE = "view_quote"
    ACCEPT_QUOTE = "accept_quote"
    REJECT_QUOTE = "reject_quote"
    UPDATE_PRICING = "update_pricing" # Installer action

class UserActivityLog(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True) # Nullable for anonymous users
    session_id = Column(String, index=True) # To track anonymous sessions
    
    event_type = Column(String, nullable=False) # EventType enum
    
    # Context specific to the event: 
    # e.g. { "product_id": 5 } for VIEW_PRODUCT
    # e.g. { "filters": { "brand": "Tesla", "min_price": 500 } } for FILTER_INVENTORY
    metadata_json = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SimulationLog(Base):
    """
    Tracks popular parameters to understand market demand trends.
    """
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    location_region = Column(String, index=True) # e.g. "VN-HN"
    
    # What did they simulate?
    solar_capacity_kw = Column(Float)
    battery_capacity_kwh = Column(Float)
    monthly_bill = Column(Float)
    
    # Result snapshot
    roi_years = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
