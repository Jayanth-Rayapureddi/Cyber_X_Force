from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RoleBase(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class DepartmentBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    location: str | None = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role_id: int
    department_id: int | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    role_id: int
    department_id: int | None
    created_at: datetime


class AssetBase(BaseModel):
    asset_code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=150)
    asset_type: str = Field(min_length=2, max_length=100)
    description: str | None = None
    location: str | None = None

    confidentiality: int = Field(default=1, ge=1, le=5)
    integrity: int = Field(default=1, ge=1, le=5)
    availability: int = Field(default=1, ge=1, le=5)

    department_id: int
    owner_id: int | None = None


class AssetCreate(AssetBase):
    pass


class AssetResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criticality: str
    is_active: bool
    created_at: datetime