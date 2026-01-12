from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.inventory import Brand, ProductModel, InventoryListing, ComponentType
from models.user import User
from schemas.inventory import (
    BrandCreate, BrandOut, 
    ProductModelCreate, ProductModelOut,
    InventoryListingCreate, InventoryListingOut,
    SolarPanelSpecs, BatterySpecs, InverterSpecs
)
from routers.v1.auth import get_db, oauth2_scheme, get_current_user # Re-using dependency
from core import security

router = APIRouter()

# --- ADMIN: Brand & Catalog Management ---

@router.post("/brands", response_model=BrandOut)
def create_brand(
    brand_in: BrandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    brand = Brand(**brand_in.dict())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand

@router.post("/products", response_model=ProductModelOut)
def create_product(
    product_in: ProductModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required")
    
    # Validate Specs based on Type
    try:
        if product_in.type == ComponentType.SOLAR_PANEL.value:
            SolarPanelSpecs(**product_in.specs)
        elif product_in.type == ComponentType.BATTERY.value:
            BatterySpecs(**product_in.specs)
        elif product_in.type == ComponentType.INVERTER.value:
            InverterSpecs(**product_in.specs)
        else:
            # warning: unknown type
            pass
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid specs for type {product_in.type}: {str(e)}")
        
    product = ProductModel(**product_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# --- INSTALLER: Inventory Management ---

@router.post("/inventory", response_model=InventoryListingOut)
def create_listing(
    listing_in: InventoryListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "installer" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Installer permissions required")
    
    # Verify product exists
    product = db.query(ProductModel).filter(ProductModel.id == listing_in.product_model_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product model not found")

    listing = InventoryListing(
        **listing_in.dict(),
        installer_id=current_user.id
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing

@router.get("/inventory/my", response_model=List[InventoryListingOut])
def read_my_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = db.query(InventoryListing).filter(InventoryListing.installer_id == current_user.id).all()
    # Eager loading might be needed in prod, here ORM default lazy load works for simple access
    return items

@router.get("/catalog", response_model=List[ProductModelOut])
def read_catalog(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ProductModel)
    if type:
        query = query.filter(ProductModel.type == type)
    return query.offset(skip).limit(limit).all()
