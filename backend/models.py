from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
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