from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime

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


# =========================================================
# Risk-Control Mappings
# =========================================================

def get_risk_control_mappings(
    db: Session,
) -> list[models.RiskControl]:
    statement = select(models.RiskControl).order_by(
        models.RiskControl.created_at.desc()
    )

    return list(db.scalars(statement).all())


def get_risk_control_mapping(
    db: Session,
    mapping_id: int,
) -> models.RiskControl | None:
    return db.get(models.RiskControl, mapping_id)


def get_mapping_by_risk_and_control(
    db: Session,
    risk_id: int,
    control_id: int,
) -> models.RiskControl | None:
    statement = select(models.RiskControl).where(
        models.RiskControl.risk_id == risk_id,
        models.RiskControl.control_id == control_id,
    )

    return db.scalar(statement)


def get_control_mappings_for_risk(
    db: Session,
    risk_id: int,
) -> list[models.RiskControl]:
    statement = (
        select(models.RiskControl)
        .where(models.RiskControl.risk_id == risk_id)
        .order_by(models.RiskControl.created_at.desc())
    )

    return list(db.scalars(statement).all())


def create_risk_control_mapping(
    db: Session,
    mapping_data: schemas.RiskControlCreate,
) -> models.RiskControl:
    mapping = models.RiskControl(
        **mapping_data.model_dump()
    )

    db.add(mapping)

    try:
        db.commit()
        db.refresh(mapping)
        return mapping

    except IntegrityError:
        db.rollback()
        raise


def update_risk_control_mapping(
    db: Session,
    mapping: models.RiskControl,
    mapping_data: schemas.RiskControlUpdate,
) -> models.RiskControl:
    update_values = mapping_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_values.items():
        setattr(mapping, field, value)

    db.commit()
    db.refresh(mapping)

    return mapping


def delete_risk_control_mapping(
    db: Session,
    mapping: models.RiskControl,
) -> None:
    db.delete(mapping)
    db.commit()


# =========================================================
# Compliance Dashboard
# =========================================================

def get_compliance_summary(db: Session):
    controls = db.scalars(
        select(models.Control)
    ).all()

    total = len(controls)

    implemented = sum(
        c.implementation_status == "Implemented"
        for c in controls
    )

    in_progress = sum(
        c.implementation_status == "In Progress"
        for c in controls
    )

    planned = sum(
        c.implementation_status == "Planned"
        for c in controls
    )

    not_started = sum(
        c.implementation_status == "Not Started"
        for c in controls
    )

    not_applicable = sum(
        c.implementation_status == "Not Applicable"
        for c in controls
    )

    applicable_controls = total - not_applicable

    if total == 0:
        compliance = 0
        average = 0

    else:
        compliance = (
            round(
                (implemented / applicable_controls) * 100,
                2,
            )
            if applicable_controls > 0
            else 0
        )

        average = round(
            sum(
                c.implementation_percentage
                for c in controls
            )
            / total,
            2,
        )

    return {
        "total_controls": total,
        "implemented": implemented,
        "in_progress": in_progress,
        "planned": planned,
        "not_started": not_started,
        "not_applicable": not_applicable,
        "overall_compliance_percentage": compliance,
        "average_implementation_percentage": average,
    }


# =========================================================
# Overdue Controls
# =========================================================

def get_overdue_controls(db: Session):

    controls = db.scalars(
        select(models.Control)
    ).all()

    now = datetime.utcnow()

    overdue = []

    for control in controls:

        if (
            control.target_date
            and control.implementation_status != "Implemented"
            and control.target_date < now
        ):

            overdue.append(
                {
                    "id": control.id,
                    "control_code": control.control_code,
                    "title": control.title,
                    "owner": control.owner,
                    "implementation_status": control.implementation_status,
                    "implementation_percentage": control.implementation_percentage,
                    "target_date": control.target_date,
                    "days_overdue": (
                        now - control.target_date
                    ).days,
                }
            )

    overdue.sort(
        key=lambda x: x["days_overdue"],
        reverse=True,
    )

    return overdue

# =========================================================
# Compliance Dashboard Analytics
# =========================================================

def get_compliance_dashboard(db: Session):
    controls = db.scalars(
        select(models.Control)
    ).all()

    summary = get_compliance_summary(db)

    statuses = [
        "Implemented",
        "In Progress",
        "Planned",
        "Not Started",
        "Not Applicable",
    ]

    status_distribution = []

    for status_name in statuses:
        count = sum(
            control.implementation_status == status_name
            for control in controls
        )

        status_distribution.append(
            {
                "status": status_name,
                "count": count,
            }
        )

    category_counts: dict[str, int] = {}

    for control in controls:
        category_counts[control.category] = (
            category_counts.get(control.category, 0) + 1
        )

    category_distribution = [
        {
            "category": category,
            "count": count,
        }
        for category, count in sorted(category_counts.items())
    ]

    overdue_controls = get_overdue_controls(db)[:5]

    return {
        "summary": summary,
        "status_distribution": status_distribution,
        "category_distribution": category_distribution,
        "top_overdue_controls": overdue_controls,
    }