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

class DepartmentUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    description: str | None = None
    location: str | None = None
    is_active: bool | None = None


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

class AssetUpdate(BaseModel):
    asset_code: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    asset_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    description: str | None = None
    location: str | None = None

    confidentiality: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )
    integrity: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )
    availability: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    department_id: int | None = None
    owner_id: int | None = None
    is_active: bool | None = None


class AssetResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    criticality: str
    is_active: bool
    created_at: datetime


    # =========================================================
# Threat Schemas
# =========================================================

class ThreatBase(BaseModel):
    threat_code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=150)
    category: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=5)
    source: str | None = None
    default_likelihood: int = Field(default=3, ge=1, le=5)


class ThreatCreate(ThreatBase):
    pass


class ThreatUpdate(BaseModel):
    threat_code: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    category: str | None = None
    description: str | None = None
    source: str | None = None
    default_likelihood: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )
    is_active: bool | None = None


class ThreatResponse(ThreatBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


# =========================================================
# Vulnerability Schemas
# =========================================================

class VulnerabilityBase(BaseModel):
    vulnerability_code: str = Field(
        min_length=2,
        max_length=50,
    )
    name: str = Field(min_length=2, max_length=150)
    category: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=5)
    severity: str = Field(default="Medium", max_length=30)
    remediation_guidance: str | None = None


class VulnerabilityCreate(VulnerabilityBase):
    pass


class VulnerabilityUpdate(BaseModel):
    vulnerability_code: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    category: str | None = None
    description: str | None = None
    severity: str | None = None
    remediation_guidance: str | None = None
    is_active: bool | None = None


class VulnerabilityResponse(VulnerabilityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


# =========================================================
# Risk Assessment Schemas
# =========================================================

class RiskAssessmentCreate(BaseModel):
    risk_code: str = Field(min_length=2, max_length=50)
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None

    asset_id: int
    threat_id: int
    vulnerability_id: int

    likelihood: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)

    treatment_option: str = Field(
        default="Mitigate",
        pattern="^(Avoid|Mitigate|Transfer|Accept)$",
    )

    treatment_description: str | None = None
    risk_owner: str | None = None
    review_date: datetime | None = None


class RiskAssessmentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
    )
    description: str | None = None

    likelihood: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )
    impact: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    treatment_option: str | None = Field(
        default=None,
        pattern="^(Avoid|Mitigate|Transfer|Accept)$",
    )

    treatment_description: str | None = None

    residual_likelihood: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )
    residual_impact: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    status: str | None = Field(
        default=None,
        pattern="^(Open|Under Treatment|Accepted|Closed)$",
    )

    risk_owner: str | None = None
    review_date: datetime | None = None


class RiskAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    risk_code: str
    title: str
    description: str | None

    asset_id: int
    threat_id: int
    vulnerability_id: int

    likelihood: int
    impact: int
    inherent_score: int
    inherent_level: str

    treatment_option: str
    treatment_description: str | None

    residual_likelihood: int | None
    residual_impact: int | None
    residual_score: int | None
    residual_level: str | None

    status: str
    risk_owner: str | None
    review_date: datetime | None

    created_at: datetime
    updated_at: datetime



# =========================================================
# ISO Control Schemas
# =========================================================

class ControlBase(BaseModel):
    control_code: str = Field(
        min_length=2,
        max_length=30,
    )

    title: str = Field(
        min_length=3,
        max_length=200,
    )

    category: str = Field(
        min_length=2,
        max_length=100,
    )

    description: str = Field(
        min_length=5,
    )

    guidance: str | None = None

    implementation_status: str = Field(
        default="Not Started",
        pattern=(
            "^(Not Started|Planned|In Progress|"
            "Implemented|Not Applicable)$"
        ),
    )

    implementation_percentage: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    owner: str | None = None
    justification: str | None = None
    target_date: datetime | None = None


class ControlCreate(ControlBase):
    pass


class ControlUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
    )

    category: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        min_length=5,
    )

    guidance: str | None = None

    implementation_status: str | None = Field(
        default=None,
        pattern=(
            "^(Not Started|Planned|In Progress|"
            "Implemented|Not Applicable)$"
        ),
    )

    implementation_percentage: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    owner: str | None = None
    justification: str | None = None
    target_date: datetime | None = None
    last_reviewed_at: datetime | None = None
    is_active: bool | None = None


class ControlResponse(ControlBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_reviewed_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# =========================================================
# Risk-Control Mapping Schemas
# =========================================================

class RiskControlCreate(BaseModel):
    risk_id: int
    control_id: int

    mapping_justification: str = Field(
        min_length=5,
    )

    implementation_status: str = Field(
        default="Planned",
        pattern=(
            "^(Planned|In Progress|Implemented|"
            "Not Applicable)$"
        ),
    )

    effectiveness_rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    planned_start_date: datetime | None = None
    target_completion_date: datetime | None = None
    implemented_at: datetime | None = None
    notes: str | None = None


class RiskControlUpdate(BaseModel):
    mapping_justification: str | None = Field(
        default=None,
        min_length=5,
    )

    implementation_status: str | None = Field(
        default=None,
        pattern=(
            "^(Planned|In Progress|Implemented|"
            "Not Applicable)$"
        ),
    )

    effectiveness_rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    planned_start_date: datetime | None = None
    target_completion_date: datetime | None = None
    implemented_at: datetime | None = None
    notes: str | None = None


class RiskControlResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    risk_id: int
    control_id: int

    mapping_justification: str
    implementation_status: str
    effectiveness_rating: int | None

    planned_start_date: datetime | None
    target_completion_date: datetime | None
    implemented_at: datetime | None
    notes: str | None

    created_at: datetime
    updated_at: datetime


class RiskControlDetailedResponse(RiskControlResponse):
    risk_code: str
    risk_title: str
    control_code: str
    control_title: str



# =========================================================
# Compliance Dashboard
# =========================================================

class ComplianceSummaryResponse(BaseModel):
    total_controls: int

    implemented: int
    in_progress: int
    planned: int
    not_started: int
    not_applicable: int

    overall_compliance_percentage: float
    average_implementation_percentage: float



# =========================================================
# Overdue Controls
# =========================================================

class OverdueControlResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    control_code: str
    title: str

    owner: str | None

    implementation_status: str

    implementation_percentage: int

    target_date: datetime

    days_overdue: int

    # Compliance Dashboard Analytics
# =========================================================

class ComplianceStatusItem(BaseModel):
    status: str
    count: int


class ComplianceCategoryItem(BaseModel):
    category: str
    count: int


class ComplianceDashboardResponse(BaseModel):
    summary: ComplianceSummaryResponse
    status_distribution: list[ComplianceStatusItem]
    category_distribution: list[ComplianceCategoryItem]
    top_overdue_controls: list[OverdueControlResponse]