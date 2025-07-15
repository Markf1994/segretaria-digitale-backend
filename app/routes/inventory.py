from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_db
from app.schemas.inventory import (
    DeviceCreate, DeviceUpdate, DeviceResponse,
    TemporarySignageCreate, TemporarySignageUpdate, TemporarySignageResponse,
    VerticalSignageCreate, VerticalSignageUpdate, VerticalSignageResponse,
    InventorySearchParams, InventoryStatsResponse
)
from app.crud.inventory import (
    create_device, get_device, get_devices, update_device, delete_device,
    create_temporary_signage, get_temporary_signage, get_temporary_signages, 
    update_temporary_signage, delete_temporary_signage,
    create_vertical_signage, get_vertical_signage, get_vertical_signages, 
    update_vertical_signage, delete_vertical_signage,
    get_inventory_stats, get_low_stock_items
)

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


# Device Routes
@router.post("/devices/", response_model=DeviceResponse)
def create_device_endpoint(device: DeviceCreate, db: Session = Depends(get_db)):
    """Create a new device."""
    return create_device(db, device)


@router.get("/devices/", response_model=List[DeviceResponse])
def get_devices_endpoint(
    search: Optional[str] = Query(None, description="Search in name, type, brand, model, serial number"),
    type: Optional[str] = Query(None, description="Filter by device type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    location: Optional[str] = Query(None, description="Filter by location"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get devices with optional search and filtering."""
    params = InventorySearchParams(
        search=search,
        type=type,
        status=status,
        location=location,
        page=page,
        page_size=page_size
    )
    return get_devices(db, params)


@router.get("/devices/{device_id}", response_model=DeviceResponse)
def get_device_endpoint(device_id: str, db: Session = Depends(get_db)):
    """Get a specific device by ID."""
    device = get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.put("/devices/{device_id}", response_model=DeviceResponse)
def update_device_endpoint(device_id: str, device: DeviceUpdate, db: Session = Depends(get_db)):
    """Update a device."""
    updated_device = update_device(db, device_id, device)
    if not updated_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return updated_device


@router.delete("/devices/{device_id}", response_model=DeviceResponse)
def delete_device_endpoint(device_id: str, db: Session = Depends(get_db)):
    """Delete a device."""
    deleted_device = delete_device(db, device_id)
    if not deleted_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return deleted_device


# Temporary Signage Routes
@router.post("/temporary-signage/", response_model=TemporarySignageResponse)
def create_temporary_signage_endpoint(signage: TemporarySignageCreate, db: Session = Depends(get_db)):
    """Create a new temporary signage."""
    return create_temporary_signage(db, signage)


@router.get("/temporary-signage/", response_model=List[TemporarySignageResponse])
def get_temporary_signages_endpoint(
    search: Optional[str] = Query(None, description="Search in name, type, description"),
    type: Optional[str] = Query(None, description="Filter by signage type"),
    location: Optional[str] = Query(None, description="Filter by location"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get temporary signages with optional search and filtering."""
    params = InventorySearchParams(
        search=search,
        type=type,
        location=location,
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    return get_temporary_signages(db, params)


@router.get("/temporary-signage/{signage_id}", response_model=TemporarySignageResponse)
def get_temporary_signage_endpoint(signage_id: str, db: Session = Depends(get_db)):
    """Get a specific temporary signage by ID."""
    signage = get_temporary_signage(db, signage_id)
    if not signage:
        raise HTTPException(status_code=404, detail="Temporary signage not found")
    return signage


@router.put("/temporary-signage/{signage_id}", response_model=TemporarySignageResponse)
def update_temporary_signage_endpoint(signage_id: str, signage: TemporarySignageUpdate, db: Session = Depends(get_db)):
    """Update a temporary signage."""
    updated_signage = update_temporary_signage(db, signage_id, signage)
    if not updated_signage:
        raise HTTPException(status_code=404, detail="Temporary signage not found")
    return updated_signage


@router.delete("/temporary-signage/{signage_id}", response_model=TemporarySignageResponse)
def delete_temporary_signage_endpoint(signage_id: str, db: Session = Depends(get_db)):
    """Delete a temporary signage."""
    deleted_signage = delete_temporary_signage(db, signage_id)
    if not deleted_signage:
        raise HTTPException(status_code=404, detail="Temporary signage not found")
    return deleted_signage


# Vertical Signage Routes
@router.post("/vertical-signage/", response_model=VerticalSignageResponse)
def create_vertical_signage_endpoint(signage: VerticalSignageCreate, db: Session = Depends(get_db)):
    """Create a new vertical signage."""
    return create_vertical_signage(db, signage)


@router.get("/vertical-signage/", response_model=List[VerticalSignageResponse])
def get_vertical_signages_endpoint(
    search: Optional[str] = Query(None, description="Search in name, type, code, description, street_name"),
    type: Optional[str] = Query(None, description="Filter by signage type"),
    location: Optional[str] = Query(None, description="Filter by location"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get vertical signages with optional search and filtering."""
    params = InventorySearchParams(
        search=search,
        type=type,
        location=location,
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    return get_vertical_signages(db, params)


@router.get("/vertical-signage/{signage_id}", response_model=VerticalSignageResponse)
def get_vertical_signage_endpoint(signage_id: str, db: Session = Depends(get_db)):
    """Get a specific vertical signage by ID."""
    signage = get_vertical_signage(db, signage_id)
    if not signage:
        raise HTTPException(status_code=404, detail="Vertical signage not found")
    return signage


@router.put("/vertical-signage/{signage_id}", response_model=VerticalSignageResponse)
def update_vertical_signage_endpoint(signage_id: str, signage: VerticalSignageUpdate, db: Session = Depends(get_db)):
    """Update a vertical signage."""
    updated_signage = update_vertical_signage(db, signage_id, signage)
    if not updated_signage:
        raise HTTPException(status_code=404, detail="Vertical signage not found")
    return updated_signage


@router.delete("/vertical-signage/{signage_id}", response_model=VerticalSignageResponse)
def delete_vertical_signage_endpoint(signage_id: str, db: Session = Depends(get_db)):
    """Delete a vertical signage."""
    deleted_signage = delete_vertical_signage(db, signage_id)
    if not deleted_signage:
        raise HTTPException(status_code=404, detail="Vertical signage not found")
    return deleted_signage


# Statistics and Dashboard Routes
@router.get("/stats/", response_model=InventoryStatsResponse)
def get_inventory_stats_endpoint(db: Session = Depends(get_db)):
    """Get inventory statistics."""
    stats = get_inventory_stats(db)
    return InventoryStatsResponse(**stats)


@router.get("/low-stock/")
def get_low_stock_items_endpoint(db: Session = Depends(get_db)):
    """Get items with low stock."""
    return get_low_stock_items(db)