import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session
from db.session import SessionLocal, engine
from models import inventory, user
from models.inventory import Brand, ProductModel, ComponentType

def seed_data():
    db = SessionLocal()
    
    # 1. Brands
    brands = [
        {"name": "Tesla", "origin_country": "USA", "tier": "Premium"},
        {"name": "LG Energy", "origin_country": "South Korea", "tier": "Tier 1"},
        {"name": "Canadian Solar", "origin_country": "Canada/China", "tier": "Tier 1"},
        {"name": "Huawei", "origin_country": "China", "tier": "Tier 1"},
        {"name": "SMA", "origin_country": "Germany", "tier": "Premium"},
        {"name": "Longi", "origin_country": "China", "tier": "Tier 1"},
    ]
    
    brand_map = {}
    for b_data in brands:
        existing = db.query(Brand).filter(Brand.name == b_data["name"]).first()
        if not existing:
            brand = Brand(**b_data)
            db.add(brand)
            db.commit()
            db.refresh(brand)
            brand_map[brand.name] = brand
            print(f"Created Brand: {brand.name}")
        else:
            brand_map[existing.name] = existing

    # 2. Products (Panels)
    panels = [
        {
            "model_number": "HiKu6 Mono 450W",
            "brand_id": brand_map["Canadian Solar"].id,
            "type": ComponentType.SOLAR_PANEL,
            "specs": {"power_w": 450, "efficiency": 0.21, "dimensions": "2x1m"},
            "warranty_years": 25
        },
        {
            "model_number": "Hi-MO 5 540W",
            "brand_id": brand_map["Longi"].id,
            "type": ComponentType.SOLAR_PANEL,
            "specs": {"power_w": 540, "efficiency": 0.215, "dimensions": "2.2x1.1m"},
            "warranty_years": 25
        }
    ]
    
    # 3. Products (Batteries)
    batteries = [
        {
            "model_number": "Powerwall 2",
            "brand_id": brand_map["Tesla"].id,
            "type": ComponentType.BATTERY,
            "specs": {"capacity_kwh": 13.5, "max_power_kw": 5.0, "voltage": 240, "technology": "NMC"},
            "warranty_years": 10
        },
        {
            "model_number": "RESU 10H",
            "brand_id": brand_map["LG Energy"].id,
            "type": ComponentType.BATTERY,
            "specs": {"capacity_kwh": 9.8, "max_power_kw": 5.0, "voltage": 400, "technology": "NMC"},
            "warranty_years": 10
        }
    ]
    
    # 4. Products (Inverters)
    inverters = [
        {
            "model_number": "Sunny Boy 5.0",
            "brand_id": brand_map["SMA"].id,
            "type": ComponentType.INVERTER,
            "specs": {"max_output_kw": 5.0, "efficiency": 0.97, "phases": 1, "hybrid": False},
            "warranty_years": 10
        },
        {
            "model_number": "SUN2000-10KTL",
            "brand_id": brand_map["Huawei"].id,
            "type": ComponentType.INVERTER,
            "specs": {"max_output_kw": 10.0, "efficiency": 0.98, "phases": 3, "hybrid": True},
            "warranty_years": 10
        }
    ]
    
    all_products = panels + batteries + inverters
    
    for p_data in all_products:
        existing = db.query(ProductModel).filter(ProductModel.model_number == p_data["model_number"]).first()
        if not existing:
            prod = ProductModel(**p_data)
            db.add(prod)
            db.commit()
            print(f"Created Product: {prod.model_number}")
            
    db.close()

if __name__ == "__main__":
    seed_data()
