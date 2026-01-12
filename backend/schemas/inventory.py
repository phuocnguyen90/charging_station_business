from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator

# --- Core Specs ---
class BaseComponentSpecs(BaseModel):
    manufacturer: Optional[str] = None # Helper if brand is not joined
    weight_kg: Optional[float] = None
    dimensions_mm: Optional[Dict[str, float]] = None # {l, w, h}

class SolarPanelSpecs(BaseComponentSpecs):
    wattage: float = Field(..., gt=0)
    efficiency: float = Field(..., gt=0, lt=1.0)
    cell_type: Optional[str] = "Monocrystalline"
    bifacial: bool = False

class BatterySpecs(BaseComponentSpecs):
    capacity_kwh: float = Field(..., gt=0)
    voltage_nominal: float = 48.0
    chemistry: str # LFP, NMC
    max_discharge_kw: float
    depth_of_discharge: float = 0.9

class InverterSpecs(BaseComponentSpecs):
    max_input_voltage: float
    rated_power_kw: float
    phases: int = 1 # 1 or 3
    type: str # String, Hybrid, Micro

# --- Database Models DTOs ---

class BrandBase(BaseModel):
    name: str
    origin_country: Optional[str] = None
    tier: str = "Standard"

class BrandCreate(BrandBase):
    pass

class BrandOut(BrandBase):
    id: int
    class Config:
        from_attributes = True

class ProductModelCreate(BaseModel):
    brand_id: int
    model_number: str
    type: str 
    # Client sends generic dict; backend validates logic inside service
    specs: Dict[str, Any] 
    datasheet_url: Optional[str] = None
    warranty_years: int = 10

class ProductModelOut(ProductModelCreate):
    id: int
    class Config:
        from_attributes = True

class InventoryListingCreate(BaseModel):
    product_model_id: int
    cost_price: Optional[float] = None
    base_price: float
    currency: str = "USD"
    is_public: bool = True
    regional_pricing: Optional[Dict[str, float]] = {}
    stock_level: int = 0

class InventoryListingOut(InventoryListingCreate):
    id: int
    installer_id: int
    # We allow including related objects for convenience
    product: Optional[ProductModelOut] = None

    class Config:
        from_attributes = True
