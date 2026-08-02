from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="role",
    )


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="department",
    )

    assets: Mapped[list["Asset"]] = relationship(
        back_populates="department",
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False,
    )

    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    role: Mapped["Role"] = relationship(
        back_populates="users",
    )

    department: Mapped["Department | None"] = relationship(
        back_populates="users",
    )

    owned_assets: Mapped[list["Asset"]] = relationship(
        back_populates="owner",
    )


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    asset_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    asset_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    confidentiality: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    integrity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    availability: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    criticality: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Low",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"),
        nullable=False,
    )

    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    department: Mapped["Department"] = relationship(
        back_populates="assets",
    )

    owner: Mapped["User | None"] = relationship(
        back_populates="owned_assets",
    )


class Threat(Base):
    __tablename__ = "threats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    threat_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    default_likelihood: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    risks: Mapped[list["RiskAssessment"]] = relationship(
        back_populates="threat",
    )


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    vulnerability_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(30),
        default="Medium",
        nullable=False,
    )

    remediation_guidance: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    risks: Mapped[list["RiskAssessment"]] = relationship(
        back_populates="vulnerability",
    )

class Control(Base):
    __tablename__ = "controls"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    control_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    guidance: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    implementation_status: Mapped[str] = mapped_column(
        String(30),
        default="Not Started",
        nullable=False,
    )

    implementation_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    owner: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    justification: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    target_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    risk_mappings: Mapped[list["RiskControl"]] = relationship(
        back_populates="control",
        cascade="all, delete-orphan",
    )

    assessments: Mapped[list["ComplianceAssessment"]] = relationship(
        back_populates="control",
        cascade="all, delete-orphan",
    )

    evidence_records: Mapped[list["Evidence"]] = relationship(
        back_populates="control",
        cascade="all, delete-orphan",
    )


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    risk_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        nullable=False,
    )

    threat_id: Mapped[int] = mapped_column(
        ForeignKey("threats.id"),
        nullable=False,
    )

    vulnerability_id: Mapped[int] = mapped_column(
        ForeignKey("vulnerabilities.id"),
        nullable=False,
    )

    likelihood: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    impact: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    inherent_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    inherent_level: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    treatment_option: Mapped[str] = mapped_column(
        String(30),
        default="Mitigate",
        nullable=False,
    )

    treatment_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    residual_likelihood: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    residual_impact: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    residual_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    residual_level: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Open",
        nullable=False,
    )

    risk_owner: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    review_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    asset: Mapped["Asset"] = relationship()
    threat: Mapped["Threat"] = relationship(
        back_populates="risks",
    )
    vulnerability: Mapped["Vulnerability"] = relationship(
        back_populates="risks",
    )

    control_mappings: Mapped[list["RiskControl"]] = relationship(
        back_populates="risk",
        cascade="all, delete-orphan",
    )



class RiskControl(Base):
    __tablename__ = "risk_controls"

    __table_args__ = (
        UniqueConstraint(
            "risk_id",
            "control_id",
            name="uq_risk_control_mapping",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    risk_id: Mapped[int] = mapped_column(
        ForeignKey(
            "risk_assessments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    control_id: Mapped[int] = mapped_column(
        ForeignKey(
            "controls.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    mapping_justification: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    implementation_status: Mapped[str] = mapped_column(
        String(30),
        default="Planned",
        nullable=False,
    )

    effectiveness_rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    planned_start_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    target_completion_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    implemented_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    risk: Mapped["RiskAssessment"] = relationship(
        back_populates="control_mappings",
    )

    control: Mapped["Control"] = relationship(
        back_populates="risk_mappings",
    )

# =========================================================
# Compliance Assessments and Evidence
# =========================================================

class ComplianceAssessment(Base):
    __tablename__ = "compliance_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    assessment_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    control_id: Mapped[int] = mapped_column(
        ForeignKey("controls.id", ondelete="CASCADE"), nullable=False, index=True
    )
    compliance_status: Mapped[str] = mapped_column(
        String(30), default="Not Assessed", nullable=False
    )
    compliance_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    assessor: Mapped[str] = mapped_column(String(150), nullable=False)
    assessment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    findings: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_review_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    control: Mapped["Control"] = relationship(back_populates="assessments")
    evidence_records: Mapped[list["Evidence"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    evidence_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_location: Mapped[str] = mapped_column(Text, nullable=False)
    control_id: Mapped[int | None] = mapped_column(
        ForeignKey("controls.id", ondelete="CASCADE"), nullable=True, index=True
    )
    assessment_id: Mapped[int | None] = mapped_column(
        ForeignKey("compliance_assessments.id", ondelete="CASCADE"), nullable=True, index=True
    )
    owner: Mapped[str | None] = mapped_column(String(150), nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    control: Mapped["Control | None"] = relationship(back_populates="evidence_records")
    assessment: Mapped["ComplianceAssessment | None"] = relationship(
        back_populates="evidence_records"
    )


# =========================================================
# Internal Audits and Corrective Actions
# =========================================================

class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    audit_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    audit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    scope: Mapped[str] = mapped_column(Text, nullable=False)
    lead_auditor: Mapped[str] = mapped_column(String(150), nullable=False)
    planned_start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    planned_end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="Planned", nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    findings: Mapped[list["AuditFinding"]] = relationship(
        back_populates="audit", cascade="all, delete-orphan"
    )


class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    finding_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    audit_id: Mapped[int] = mapped_column(
        ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    control_id: Mapped[int | None] = mapped_column(
        ForeignKey("controls.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    finding_type: Mapped[str] = mapped_column(String(40), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner: Mapped[str | None] = mapped_column(String(150), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="Open", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    audit: Mapped["Audit"] = relationship(back_populates="findings")
    corrective_actions: Mapped[list["CorrectiveAction"]] = relationship(
        back_populates="finding", cascade="all, delete-orphan"
    )


class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    action_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    finding_id: Mapped[int] = mapped_column(
        ForeignKey("audit_findings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action_description: Mapped[str] = mapped_column(Text, nullable=False)
    action_owner: Mapped[str] = mapped_column(String(150), nullable=False)
    target_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="Open", nullable=False)
    completion_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    verification_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    finding: Mapped["AuditFinding"] = relationship(back_populates="corrective_actions")


# =========================================================
# Incident Management
# =========================================================

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    asset_id: Mapped[int | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    reported_by: Mapped[str] = mapped_column(String(150), nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(String(150), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="Reported", nullable=False)
    containment_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    lessons_learned: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    asset: Mapped["Asset | None"] = relationship()
    actions: Mapped[list["IncidentAction"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan"
    )


class IncidentAction(Base):
    __tablename__ = "incident_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    performed_by: Mapped[str] = mapped_column(String(150), nullable=False)
    performed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    incident: Mapped["Incident"] = relationship(back_populates="actions")
