from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
import schemas


# =========================================================
# Roles
# =========================================================

def get_roles(db: Session) -> list[models.Role]:
    statement = select(models.Role).order_by(models.Role.name)
    return list(db.scalars(statement).all())


def get_role(db: Session, role_id: int) -> models.Role | None:
    return db.get(models.Role, role_id)


def get_role_by_name(db: Session, name: str) -> models.Role | None:
    statement = select(models.Role).where(models.Role.name == name)
    return db.scalar(statement)


def create_role(
    db: Session,
    role_data: schemas.RoleCreate,
) -> models.Role:
    role = models.Role(**role_data.model_dump())

    db.add(role)

    try:
        db.commit()
        db.refresh(role)
        return role

    except IntegrityError:
        db.rollback()
        raise


# =========================================================
# Departments
# =========================================================

def get_departments(db: Session) -> list[models.Department]:
    statement = select(models.Department).order_by(
        models.Department.name
    )
    return list(db.scalars(statement).all())


def get_department(
    db: Session,
    department_id: int,
) -> models.Department | None:
    return db.get(models.Department, department_id)


def get_department_by_name(
    db: Session,
    name: str,
) -> models.Department | None:
    statement = select(models.Department).where(
        models.Department.name == name
    )
    return db.scalar(statement)


def create_department(
    db: Session,
    department_data: schemas.DepartmentCreate,
) -> models.Department:
    department = models.Department(
        **department_data.model_dump()
    )

    db.add(department)

    try:
        db.commit()
        db.refresh(department)
        return department

    except IntegrityError:
        db.rollback()
        raise


# =========================================================
# Assets
# =========================================================

def calculate_asset_criticality(
    confidentiality: int,
    integrity: int,
    availability: int,
) -> str:
    """
    Calculate asset criticality using the average CIA score.
    """

    average_score = (
        confidentiality + integrity + availability
    ) / 3

    if average_score >= 4.5:
        return "Critical"

    if average_score >= 3.5:
        return "High"

    if average_score >= 2.5:
        return "Medium"

    return "Low"


def get_assets(db: Session) -> list[models.Asset]:
    statement = select(models.Asset).order_by(
        models.Asset.asset_code
    )
    return list(db.scalars(statement).all())


def get_asset(
    db: Session,
    asset_id: int,
) -> models.Asset | None:
    return db.get(models.Asset, asset_id)


def get_asset_by_code(
    db: Session,
    asset_code: str,
) -> models.Asset | None:
    statement = select(models.Asset).where(
        models.Asset.asset_code == asset_code
    )
    return db.scalar(statement)


def create_asset(
    db: Session,
    asset_data: schemas.AssetCreate,
) -> models.Asset:
    criticality = calculate_asset_criticality(
        confidentiality=asset_data.confidentiality,
        integrity=asset_data.integrity,
        availability=asset_data.availability,
    )

    asset = models.Asset(
        **asset_data.model_dump(),
        criticality=criticality,
    )

    db.add(asset)

    try:
        db.commit()
        db.refresh(asset)
        return asset

    except IntegrityError:
        db.rollback()
        raise


def delete_asset(
    db: Session,
    asset: models.Asset,
) -> None:
    db.delete(asset)
    db.commit()

# =========================================================
# Threats
# =========================================================

def get_threats(db: Session) -> list[models.Threat]:
    statement = select(models.Threat).order_by(
        models.Threat.threat_code
    )
    return list(db.scalars(statement).all())


def get_threat(
    db: Session,
    threat_id: int,
) -> models.Threat | None:
    return db.get(models.Threat, threat_id)


def get_threat_by_code(
    db: Session,
    threat_code: str,
) -> models.Threat | None:
    statement = select(models.Threat).where(
        models.Threat.threat_code == threat_code
    )
    return db.scalar(statement)


def create_threat(
    db: Session,
    threat_data: schemas.ThreatCreate,
) -> models.Threat:
    threat = models.Threat(**threat_data.model_dump())

    db.add(threat)

    try:
        db.commit()
        db.refresh(threat)
        return threat

    except IntegrityError:
        db.rollback()
        raise


# =========================================================
# Vulnerabilities
# =========================================================

def get_vulnerabilities(
    db: Session,
) -> list[models.Vulnerability]:
    statement = select(models.Vulnerability).order_by(
        models.Vulnerability.vulnerability_code
    )
    return list(db.scalars(statement).all())


def get_vulnerability(
    db: Session,
    vulnerability_id: int,
) -> models.Vulnerability | None:
    return db.get(models.Vulnerability, vulnerability_id)


def get_vulnerability_by_code(
    db: Session,
    vulnerability_code: str,
) -> models.Vulnerability | None:
    statement = select(models.Vulnerability).where(
        models.Vulnerability.vulnerability_code
        == vulnerability_code
    )
    return db.scalar(statement)


def create_vulnerability(
    db: Session,
    vulnerability_data: schemas.VulnerabilityCreate,
) -> models.Vulnerability:
    vulnerability = models.Vulnerability(
        **vulnerability_data.model_dump()
    )

    db.add(vulnerability)

    try:
        db.commit()
        db.refresh(vulnerability)
        return vulnerability

    except IntegrityError:
        db.rollback()
        raise


# =========================================================
# Risk Assessments
# =========================================================

def calculate_risk_score(
    likelihood: int,
    impact: int,
) -> int:
    return likelihood * impact


def calculate_risk_level(score: int) -> str:
    if score >= 17:
        return "Critical"

    if score >= 10:
        return "High"

    if score >= 5:
        return "Medium"

    return "Low"


def get_risk_assessments(
    db: Session,
) -> list[models.RiskAssessment]:
    statement = select(models.RiskAssessment).order_by(
        models.RiskAssessment.created_at.desc()
    )
    return list(db.scalars(statement).all())


def get_risk_assessment(
    db: Session,
    risk_id: int,
) -> models.RiskAssessment | None:
    return db.get(models.RiskAssessment, risk_id)


def get_risk_by_code(
    db: Session,
    risk_code: str,
) -> models.RiskAssessment | None:
    statement = select(models.RiskAssessment).where(
        models.RiskAssessment.risk_code == risk_code
    )
    return db.scalar(statement)


def create_risk_assessment(
    db: Session,
    risk_data: schemas.RiskAssessmentCreate,
) -> models.RiskAssessment:
    inherent_score = calculate_risk_score(
        likelihood=risk_data.likelihood,
        impact=risk_data.impact,
    )

    inherent_level = calculate_risk_level(
        inherent_score
    )

    risk = models.RiskAssessment(
        **risk_data.model_dump(),
        inherent_score=inherent_score,
        inherent_level=inherent_level,
    )

    db.add(risk)

    try:
        db.commit()
        db.refresh(risk)
        return risk

    except IntegrityError:
        db.rollback()
        raise



# =========================================================
# ISO Controls
# =========================================================

def get_controls(
    db: Session,
) -> list[models.Control]:
    statement = select(models.Control).order_by(
        models.Control.control_code
    )
    return list(db.scalars(statement).all())


def get_control(
    db: Session,
    control_id: int,
) -> models.Control | None:
    return db.get(models.Control, control_id)


def get_control_by_code(
    db: Session,
    control_code: str,
) -> models.Control | None:
    statement = select(models.Control).where(
        models.Control.control_code == control_code
    )
    return db.scalar(statement)


def create_control(
    db: Session,
    control_data: schemas.ControlCreate,
) -> models.Control:
    control = models.Control(
        **control_data.model_dump()
    )

    db.add(control)

    try:
        db.commit()
        db.refresh(control)
        return control

    except IntegrityError:
        db.rollback()
        raise