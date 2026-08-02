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

# =========================================================
# Compliance Assessments and Evidence
# =========================================================

class ComplianceAssessmentCreate(BaseModel):
    assessment_code: str = Field(min_length=2, max_length=50)
    control_id: int
    compliance_status: str = Field(
        default="Not Assessed",
        pattern="^(Not Assessed|Compliant|Partially Compliant|Non-Compliant|Not Applicable)$",
    )
    compliance_score: int = Field(default=0, ge=0, le=100)
    assessor: str = Field(min_length=2, max_length=150)
    assessment_date: datetime
    findings: str | None = None
    recommendations: str | None = None
    evidence_reference: str | None = None
    next_review_date: datetime | None = None


class ComplianceAssessmentUpdate(BaseModel):
    compliance_status: str | None = Field(
        default=None,
        pattern="^(Not Assessed|Compliant|Partially Compliant|Non-Compliant|Not Applicable)$",
    )
    compliance_score: int | None = Field(default=None, ge=0, le=100)
    assessor: str | None = Field(default=None, min_length=2, max_length=150)
    assessment_date: datetime | None = None
    findings: str | None = None
    recommendations: str | None = None
    evidence_reference: str | None = None
    next_review_date: datetime | None = None


class ComplianceAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    assessment_code: str
    control_id: int
    compliance_status: str
    compliance_score: int
    assessor: str
    assessment_date: datetime
    findings: str | None
    recommendations: str | None
    evidence_reference: str | None
    next_review_date: datetime | None
    created_at: datetime
    updated_at: datetime


class EvidenceCreate(BaseModel):
    evidence_code: str = Field(min_length=2, max_length=50)
    title: str = Field(min_length=3, max_length=200)
    evidence_type: str = Field(min_length=2, max_length=50)
    description: str | None = None
    reference_location: str = Field(min_length=2)
    control_id: int | None = None
    assessment_id: int | None = None
    owner: str | None = None
    collected_at: datetime
    valid_until: datetime | None = None
    is_verified: bool = False
    verification_notes: str | None = None


class EvidenceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    evidence_type: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = None
    reference_location: str | None = Field(default=None, min_length=2)
    owner: str | None = None
    collected_at: datetime | None = None
    valid_until: datetime | None = None
    is_verified: bool | None = None
    verification_notes: str | None = None


class EvidenceResponse(EvidenceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


# =========================================================
# Audits, Findings and Corrective Actions
# =========================================================

class AuditCreate(BaseModel):
    audit_code: str = Field(min_length=2, max_length=50)
    title: str = Field(min_length=3, max_length=200)
    audit_type: str = Field(min_length=2, max_length=50)
    scope: str = Field(min_length=5)
    lead_auditor: str = Field(min_length=2, max_length=150)
    planned_start_date: datetime
    planned_end_date: datetime
    status: str = Field(default="Planned", pattern="^(Planned|In Progress|Completed|Cancelled)$")
    summary: str | None = None


class AuditUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    audit_type: str | None = None
    scope: str | None = None
    lead_auditor: str | None = None
    planned_start_date: datetime | None = None
    planned_end_date: datetime | None = None
    status: str | None = Field(default=None, pattern="^(Planned|In Progress|Completed|Cancelled)$")
    summary: str | None = None


class AuditResponse(AuditCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class AuditFindingCreate(BaseModel):
    finding_code: str = Field(min_length=2, max_length=50)
    audit_id: int
    control_id: int | None = None
    title: str = Field(min_length=3, max_length=200)
    finding_type: str = Field(pattern="^(Observation|Opportunity for Improvement|Minor Non-Conformity|Major Non-Conformity)$")
    severity: str = Field(pattern="^(Low|Medium|High|Critical)$")
    description: str = Field(min_length=5)
    root_cause: str | None = None
    owner: str | None = None
    due_date: datetime | None = None
    status: str = Field(default="Open", pattern="^(Open|Under Review|Remediation|Verified|Closed)$")


class AuditFindingUpdate(BaseModel):
    title: str | None = None
    finding_type: str | None = Field(default=None, pattern="^(Observation|Opportunity for Improvement|Minor Non-Conformity|Major Non-Conformity)$")
    severity: str | None = Field(default=None, pattern="^(Low|Medium|High|Critical)$")
    description: str | None = None
    root_cause: str | None = None
    owner: str | None = None
    due_date: datetime | None = None
    status: str | None = Field(default=None, pattern="^(Open|Under Review|Remediation|Verified|Closed)$")


class AuditFindingResponse(AuditFindingCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class CorrectiveActionCreate(BaseModel):
    action_code: str = Field(min_length=2, max_length=50)
    finding_id: int
    action_description: str = Field(min_length=5)
    action_owner: str = Field(min_length=2, max_length=150)
    target_date: datetime
    status: str = Field(default="Open", pattern="^(Open|In Progress|Completed|Verified|Cancelled)$")
    completion_percentage: int = Field(default=0, ge=0, le=100)
    completion_date: datetime | None = None
    verification_result: str | None = None


class CorrectiveActionUpdate(BaseModel):
    action_description: str | None = None
    action_owner: str | None = None
    target_date: datetime | None = None
    status: str | None = Field(default=None, pattern="^(Open|In Progress|Completed|Verified|Cancelled)$")
    completion_percentage: int | None = Field(default=None, ge=0, le=100)
    completion_date: datetime | None = None
    verification_result: str | None = None


class CorrectiveActionResponse(CorrectiveActionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


# =========================================================
# Incident Management
# =========================================================

class IncidentCreate(BaseModel):
    incident_code: str = Field(min_length=2, max_length=50)
    title: str = Field(min_length=3, max_length=200)
    category: str = Field(min_length=2, max_length=100)
    severity: str = Field(pattern="^(Low|Medium|High|Critical)$")
    description: str = Field(min_length=5)
    asset_id: int | None = None
    reported_by: str = Field(min_length=2, max_length=150)
    assigned_to: str | None = None
    detected_at: datetime
    status: str = Field(default="Reported", pattern="^(Reported|Triaged|Investigating|Contained|Recovered|Closed)$")
    containment_summary: str | None = None
    root_cause: str | None = None
    lessons_learned: str | None = None
    closed_at: datetime | None = None


class IncidentUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    severity: str | None = Field(default=None, pattern="^(Low|Medium|High|Critical)$")
    description: str | None = None
    assigned_to: str | None = None
    status: str | None = Field(default=None, pattern="^(Reported|Triaged|Investigating|Contained|Recovered|Closed)$")
    containment_summary: str | None = None
    root_cause: str | None = None
    lessons_learned: str | None = None
    closed_at: datetime | None = None


class IncidentResponse(IncidentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class IncidentActionCreate(BaseModel):
    incident_id: int
    action_type: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=5)
    performed_by: str = Field(min_length=2, max_length=150)
    performed_at: datetime


class IncidentActionResponse(IncidentActionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class ManagementDashboardResponse(BaseModel):
    total_assets: int
    total_risks: int
    critical_risks: int
    open_incidents: int
    open_audit_findings: int
    overdue_corrective_actions: int
    compliance_percentage: float
