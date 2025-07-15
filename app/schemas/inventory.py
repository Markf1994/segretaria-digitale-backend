from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Device Schemas
class DeviceCreate(BaseModel):
    name: str
    type: str
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    status: str = "disponibile"
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    status: Optional[str] = None
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class DeviceResponse(BaseModel):
    id: str
    name: str
    type: str
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    status: str
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


# TemporarySignage Schemas
class TemporarySignageCreate(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    quantity: int = 0
    min_quantity: int = 0
    location: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None


class TemporarySignageUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    min_quantity: Optional[int] = None
    location: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class TemporarySignageResponse(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str] = None
    quantity: int
    min_quantity: int
    location: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


# VerticalSignage Schemas
class VerticalSignageCreate(BaseModel):
    name: str
    type: str
    code: Optional[str] = None
    description: Optional[str] = None
    quantity: int = 0
    min_quantity: int = 0
    location: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    street_name: Optional[str] = None
    installation_date: Optional[datetime] = None
    is_active: bool = True
    notes: Optional[str] = None


class VerticalSignageUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    min_quantity: Optional[int] = None
    location: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    street_name: Optional[str] = None
    installation_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class VerticalSignageResponse(BaseModel):
    id: str
    name: str
    type: str
    code: Optional[str] = None
    description: Optional[str] = None
    quantity: int
    min_quantity: int
    location: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    street_name: Optional[str] = None
    installation_date: Optional[datetime] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


# Search and Filter Schemas
class InventorySearchParams(BaseModel):
    search: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
    page: int = 1
    page_size: int = 50


class InventoryStatsResponse(BaseModel):
    total_devices: int
    total_temporary_signage: int
    total_vertical_signage: int
    devices_by_status: dict
    low_stock_temporary: int
    low_stock_vertical: int