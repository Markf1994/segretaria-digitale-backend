from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.models.inventory import Device, TemporarySignage, VerticalSignage
from app.schemas.inventory import (
    DeviceCreate, DeviceUpdate,
    TemporarySignageCreate, TemporarySignageUpdate,
    VerticalSignageCreate, VerticalSignageUpdate,
    InventorySearchParams
)
from typing import List, Optional, Dict, Any
from datetime import datetime


# Device CRUD Operations
def create_device(db: Session, device: DeviceCreate) -> Device:
    """Create a new device."""
    db_device = Device(**device.dict())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_device(db: Session, device_id: str) -> Optional[Device]:
    """Get a device by ID."""
    return db.query(Device).filter(Device.id == device_id).first()


def get_devices(db: Session, params: InventorySearchParams) -> List[Device]:
    """Get devices with search and filtering."""
    query = db.query(Device)
    
    # Apply filters
    if params.search:
        search_term = f"%{params.search}%"
        query = query.filter(
            or_(
                Device.name.ilike(search_term),
                Device.type.ilike(search_term),
                Device.brand.ilike(search_term),
                Device.model.ilike(search_term),
                Device.serial_number.ilike(search_term)
            )
        )
    
    if params.type:
        query = query.filter(Device.type.ilike(f"%{params.type}%"))
    
    if params.status:
        query = query.filter(Device.status == params.status)
    
    if params.location:
        query = query.filter(Device.location.ilike(f"%{params.location}%"))
    
    # Apply pagination
    offset = (params.page - 1) * params.page_size
    return query.offset(offset).limit(params.page_size).all()


def update_device(db: Session, device_id: str, device: DeviceUpdate) -> Optional[Device]:
    """Update a device."""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if not db_device:
        return None
    
    update_data = device.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(db_device, key, value)
    
    db.commit()
    db.refresh(db_device)
    return db_device


def delete_device(db: Session, device_id: str) -> Optional[Device]:
    """Delete a device."""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if db_device:
        db.delete(db_device)
        db.commit()
    return db_device


# TemporarySignage CRUD Operations
def create_temporary_signage(db: Session, signage: TemporarySignageCreate) -> TemporarySignage:
    """Create a new temporary signage."""
    db_signage = TemporarySignage(**signage.dict())
    db.add(db_signage)
    db.commit()
    db.refresh(db_signage)
    return db_signage


def get_temporary_signage(db: Session, signage_id: str) -> Optional[TemporarySignage]:
    """Get a temporary signage by ID."""
    return db.query(TemporarySignage).filter(TemporarySignage.id == signage_id).first()


def get_temporary_signages(db: Session, params: InventorySearchParams) -> List[TemporarySignage]:
    """Get temporary signages with search and filtering."""
    query = db.query(TemporarySignage)
    
    # Apply filters
    if params.search:
        search_term = f"%{params.search}%"
        query = query.filter(
            or_(
                TemporarySignage.name.ilike(search_term),
                TemporarySignage.type.ilike(search_term),
                TemporarySignage.description.ilike(search_term)
            )
        )
    
    if params.type:
        query = query.filter(TemporarySignage.type.ilike(f"%{params.type}%"))
    
    if params.location:
        query = query.filter(TemporarySignage.location.ilike(f"%{params.location}%"))
    
    if params.is_active is not None:
        query = query.filter(TemporarySignage.is_active == params.is_active)
    
    # Apply pagination
    offset = (params.page - 1) * params.page_size
    return query.offset(offset).limit(params.page_size).all()


def update_temporary_signage(db: Session, signage_id: str, signage: TemporarySignageUpdate) -> Optional[TemporarySignage]:
    """Update a temporary signage."""
    db_signage = db.query(TemporarySignage).filter(TemporarySignage.id == signage_id).first()
    if not db_signage:
        return None
    
    update_data = signage.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(db_signage, key, value)
    
    db.commit()
    db.refresh(db_signage)
    return db_signage


def delete_temporary_signage(db: Session, signage_id: str) -> Optional[TemporarySignage]:
    """Delete a temporary signage."""
    db_signage = db.query(TemporarySignage).filter(TemporarySignage.id == signage_id).first()
    if db_signage:
        db.delete(db_signage)
        db.commit()
    return db_signage


# VerticalSignage CRUD Operations
def create_vertical_signage(db: Session, signage: VerticalSignageCreate) -> VerticalSignage:
    """Create a new vertical signage."""
    db_signage = VerticalSignage(**signage.dict())
    db.add(db_signage)
    db.commit()
    db.refresh(db_signage)
    return db_signage


def get_vertical_signage(db: Session, signage_id: str) -> Optional[VerticalSignage]:
    """Get a vertical signage by ID."""
    return db.query(VerticalSignage).filter(VerticalSignage.id == signage_id).first()


def get_vertical_signages(db: Session, params: InventorySearchParams) -> List[VerticalSignage]:
    """Get vertical signages with search and filtering."""
    query = db.query(VerticalSignage)
    
    # Apply filters
    if params.search:
        search_term = f"%{params.search}%"
        query = query.filter(
            or_(
                VerticalSignage.name.ilike(search_term),
                VerticalSignage.type.ilike(search_term),
                VerticalSignage.code.ilike(search_term),
                VerticalSignage.description.ilike(search_term),
                VerticalSignage.street_name.ilike(search_term)
            )
        )
    
    if params.type:
        query = query.filter(VerticalSignage.type.ilike(f"%{params.type}%"))
    
    if params.location:
        query = query.filter(VerticalSignage.location.ilike(f"%{params.location}%"))
    
    if params.is_active is not None:
        query = query.filter(VerticalSignage.is_active == params.is_active)
    
    # Apply pagination
    offset = (params.page - 1) * params.page_size
    return query.offset(offset).limit(params.page_size).all()


def update_vertical_signage(db: Session, signage_id: str, signage: VerticalSignageUpdate) -> Optional[VerticalSignage]:
    """Update a vertical signage."""
    db_signage = db.query(VerticalSignage).filter(VerticalSignage.id == signage_id).first()
    if not db_signage:
        return None
    
    update_data = signage.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(db_signage, key, value)
    
    db.commit()
    db.refresh(db_signage)
    return db_signage


def delete_vertical_signage(db: Session, signage_id: str) -> Optional[VerticalSignage]:
    """Delete a vertical signage."""
    db_signage = db.query(VerticalSignage).filter(VerticalSignage.id == signage_id).first()
    if db_signage:
        db.delete(db_signage)
        db.commit()
    return db_signage


# Statistics and Dashboard Functions
def get_inventory_stats(db: Session) -> Dict[str, Any]:
    """Get inventory statistics."""
    # Total counts
    total_devices = db.query(Device).count()
    total_temporary_signage = db.query(TemporarySignage).count()
    total_vertical_signage = db.query(VerticalSignage).count()
    
    # Device status counts
    device_status_counts = db.query(
        Device.status, 
        func.count(Device.id).label('count')
    ).group_by(Device.status).all()
    
    devices_by_status = {status: count for status, count in device_status_counts}
    
    # Low stock counts
    low_stock_temporary = db.query(TemporarySignage).filter(
        TemporarySignage.quantity <= TemporarySignage.min_quantity
    ).count()
    
    low_stock_vertical = db.query(VerticalSignage).filter(
        VerticalSignage.quantity <= VerticalSignage.min_quantity
    ).count()
    
    return {
        "total_devices": total_devices,
        "total_temporary_signage": total_temporary_signage,
        "total_vertical_signage": total_vertical_signage,
        "devices_by_status": devices_by_status,
        "low_stock_temporary": low_stock_temporary,
        "low_stock_vertical": low_stock_vertical
    }


def get_low_stock_items(db: Session) -> Dict[str, List]:
    """Get items with low stock."""
    low_stock_temporary = db.query(TemporarySignage).filter(
        TemporarySignage.quantity <= TemporarySignage.min_quantity
    ).all()
    
    low_stock_vertical = db.query(VerticalSignage).filter(
        VerticalSignage.quantity <= VerticalSignage.min_quantity
    ).all()
    
    return {
        "temporary_signage": low_stock_temporary,
        "vertical_signage": low_stock_vertical
    }