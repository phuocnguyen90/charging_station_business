from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from db.base import Base
import enum

class ComponentType(str, enum.Enum):
    SOLAR_PANEL = "solar_panel"
    INVERTER = "inverter"
    BATTERY = "battery"
    BOS = "balance_of_system"

class Brand(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    origin_country = Column(String, index=True) 
    tier = Column(String, default="Standard") # Tier 1, Premium, Economy

class ProductModel(Base):
    """
    The immutable technical definition of a product.
    """
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brand.id"), nullable=False)
    model_number = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False) # ComponentType string value
    
    # Strictly validated JSON spec
    specs = Column(JSON, nullable=False) 
    
    datasheet_url = Column(String, nullable=True)
    warranty_years = Column(Integer, default=10)
    
    brand = relationship("Brand", backref="products")

class InventoryListing(Base):
    """
    An installer's offering of a specific product.
    """
    id = Column(Integer, primary_key=True, index=True)
    installer_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    product_model_id = Column(Integer, ForeignKey("productmodel.id"), nullable=False)
    
    # Internal cost for installer (private)
    cost_price = Column(Float, nullable=True)
    
    # Base selling price
    base_price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    
    # Publicly visible in the marketplace?
    is_public = Column(Boolean, default=True)
    
    # Regional Pricing Overrides: { "VN": 1000, "US": 1200 }
    regional_pricing = Column(JSON, default={})
    
    stock_level = Column(Integer, default=0)
    
    product = relationship("ProductModel")
    installer = relationship("User", backref="inventory")
