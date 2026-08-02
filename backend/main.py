from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import Base, SessionLocal, engine, get_db
from seed import seed_initial_data


DatabaseSession = Annotated[Session, Depends(get_db)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_initial_data(db)

    yield


app = FastAPI(
    title="Cyber_X_Force API",
    description=(
        "ISO/IEC 27001-based Governance, Risk and Compliance "
        "API for AutoSecure Manufacturing GmbH."
    ),
    version="0.2.0",
    lifespan=lifespan,
)


# =========================================================
# General
# =========================================================

@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    return {
        "application": "Cyber_X_Force",
        "status": "running",
        "version": "0.2.0",
    }


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed.",
        )


# =========================================================
# Roles
# =========================================================

@app.get(
    "/roles",
    response_model=list[schemas.RoleResponse],
    tags=["Roles"],
)
def list_roles(db: DatabaseSession):
    return crud.get_roles(db)


@app.get(
    "/roles/{role_id}",
    response_model=schemas.RoleResponse,
    tags=["Roles"],
)
def read_role(role_id: int, db: DatabaseSession):
    role = crud.get_role(db, role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )

    return role


@app.post(
    "/roles",
    response_model=schemas.RoleResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Roles"],
)
def create_role(
    role_data: schemas.RoleCreate,
    db: DatabaseSession,
):
    existing_role = crud.get_role_by_name(
        db,
        role_data.name,
    )

    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A role with this name already exists.",
        )

    try:
        return crud.create_role(db, role_data)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create role.",
        )


# =========================================================
# Departments
# =========================================================

@app.get(
    "/departments",
    response_model=list[schemas.DepartmentResponse],
    tags=["Departments"],
)
def list_departments(db: DatabaseSession):
    return crud.get_departments(db)


@app.get(
    "/departments/{department_id}",
    response_model=schemas.DepartmentResponse,
    tags=["Departments"],
)
def read_department(
    department_id: int,
    db: DatabaseSession,
):
    department = crud.get_department(db, department_id)

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        )

    return department


@app.post(
    "/departments",
    response_model=schemas.DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Departments"],
)
def create_department(
    department_data: schemas.DepartmentCreate,
    db: DatabaseSession,
):
    existing_department = crud.get_department_by_name(
        db,
        department_data.name,
    )

    if existing_department:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A department with this name already exists."
            ),
        )

    try:
        return crud.create_department(
            db,
            department_data,
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create department.",
        )


# =========================================================
# Assets
# =========================================================

@app.get(
    "/assets",
    response_model=list[schemas.AssetResponse],
    tags=["Assets"],
)
def list_assets(db: DatabaseSession):
    return crud.get_assets(db)


@app.get(
    "/assets/{asset_id}",
    response_model=schemas.AssetResponse,
    tags=["Assets"],
)
def read_asset(asset_id: int, db: DatabaseSession):
    asset = crud.get_asset(db, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    return asset


@app.post(
    "/assets",
    response_model=schemas.AssetResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Assets"],
)
def create_asset(
    asset_data: schemas.AssetCreate,
    db: DatabaseSession,
):
    existing_asset = crud.get_asset_by_code(
        db,
        asset_data.asset_code,
    )

    if existing_asset:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An asset with this asset code already exists."
            ),
        )

    department = crud.get_department(
        db,
        asset_data.department_id,
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The selected department does not exist.",
        )

    if asset_data.owner_id is not None:
        owner = db.get(models.User, asset_data.owner_id)

        if owner is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The selected asset owner does not exist.",
            )

    try:
        return crud.create_asset(db, asset_data)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create asset.",
        )


@app.put(
    "/assets/{asset_id}",
    response_model=schemas.AssetResponse,
    tags=["Assets"],
)
def update_asset(
    asset_id: int,
    asset_data: schemas.AssetUpdate,
    db: DatabaseSession,
):
    asset = crud.get_asset(db, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    update_values = asset_data.model_dump(
        exclude_unset=True
    )

    if "department_id" in update_values:
        department = crud.get_department(
            db,
            update_values["department_id"],
        )

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The selected department does not exist.",
            )

    if "owner_id" in update_values:
        owner_id = update_values["owner_id"]

        if owner_id is not None:
            owner = db.get(models.User, owner_id)

            if owner is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The selected owner does not exist.",
                )

    for field, value in update_values.items():
        setattr(asset, field, value)

    asset.criticality = crud.calculate_asset_criticality(
        confidentiality=asset.confidentiality,
        integrity=asset.integrity,
        availability=asset.availability,
    )

    try:
        db.commit()
        db.refresh(asset)
        return asset

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Asset code already exists or the update "
                "violates a database constraint."
            ),
        )


@app.delete(
    "/assets/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Assets"],
)
def delete_asset(
    asset_id: int,
    db: DatabaseSession,
):
    asset = crud.get_asset(db, asset_id)

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    crud.delete_asset(db, asset)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# =========================================================
# Threats
# =========================================================

@app.get(
    "/threats",
    response_model=list[schemas.ThreatResponse],
    tags=["Threats"],
)
def list_threats(db: DatabaseSession):
    return crud.get_threats(db)


@app.get(
    "/threats/{threat_id}",
    response_model=schemas.ThreatResponse,
    tags=["Threats"],
)
def read_threat(
    threat_id: int,
    db: DatabaseSession,
):
    threat = crud.get_threat(db, threat_id)

    if threat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Threat not found.",
        )

    return threat


@app.post(
    "/threats",
    response_model=schemas.ThreatResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Threats"],
)
def create_threat(
    threat_data: schemas.ThreatCreate,
    db: DatabaseSession,
):
    existing_threat = crud.get_threat_by_code(
        db,
        threat_data.threat_code,
    )

    if existing_threat:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Threat code already exists.",
        )

    try:
        return crud.create_threat(db, threat_data)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create threat.",
        )




# =========================================================
# Vulnerabilities
# =========================================================

@app.get(
    "/vulnerabilities",
    response_model=list[schemas.VulnerabilityResponse],
    tags=["Vulnerabilities"],
)
def list_vulnerabilities(db: DatabaseSession):
    return crud.get_vulnerabilities(db)


@app.get(
    "/vulnerabilities/{vulnerability_id}",
    response_model=schemas.VulnerabilityResponse,
    tags=["Vulnerabilities"],
)
def read_vulnerability(
    vulnerability_id: int,
    db: DatabaseSession,
):
    vulnerability = crud.get_vulnerability(
        db,
        vulnerability_id,
    )

    if vulnerability is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vulnerability not found.",
        )

    return vulnerability


@app.post(
    "/vulnerabilities",
    response_model=schemas.VulnerabilityResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Vulnerabilities"],
)
def create_vulnerability(
    vulnerability_data: schemas.VulnerabilityCreate,
    db: DatabaseSession,
):
    existing_vulnerability = (
        crud.get_vulnerability_by_code(
            db,
            vulnerability_data.vulnerability_code,
        )
    )

    if existing_vulnerability:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vulnerability code already exists.",
        )

    try:
        return crud.create_vulnerability(
            db,
            vulnerability_data,
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create vulnerability.",
        )



# =========================================================
# Risk Assessments
# =========================================================

@app.get(
    "/risks",
    response_model=list[schemas.RiskAssessmentResponse],
    tags=["Risk Assessments"],
)
def list_risks(db: DatabaseSession):
    return crud.get_risk_assessments(db)


@app.get(
    "/risks/{risk_id}",
    response_model=schemas.RiskAssessmentResponse,
    tags=["Risk Assessments"],
)
def read_risk(
    risk_id: int,
    db: DatabaseSession,
):
    risk = crud.get_risk_assessment(db, risk_id)

    if risk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found.",
        )

    return risk


@app.post(
    "/risks",
    response_model=schemas.RiskAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Risk Assessments"],
)
def create_risk(
    risk_data: schemas.RiskAssessmentCreate,
    db: DatabaseSession,
):
    if crud.get_risk_by_code(db, risk_data.risk_code):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Risk code already exists.",
        )

    if crud.get_asset(db, risk_data.asset_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected asset does not exist.",
        )

    if crud.get_threat(db, risk_data.threat_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected threat does not exist.",
        )

    if (
        crud.get_vulnerability(
            db,
            risk_data.vulnerability_id,
        )
        is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected vulnerability does not exist.",
        )

    try:
        return crud.create_risk_assessment(
            db,
            risk_data,
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create risk assessment.",
        )


@app.put(
    "/risks/{risk_id}",
    response_model=schemas.RiskAssessmentResponse,
    tags=["Risk Assessments"],
)
def update_risk(
    risk_id: int,
    risk_data: schemas.RiskAssessmentUpdate,
    db: DatabaseSession,
):
    risk = crud.get_risk_assessment(db, risk_id)

    if risk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found.",
        )

    update_values = risk_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_values.items():
        setattr(risk, field, value)

    risk.inherent_score = crud.calculate_risk_score(
        likelihood=risk.likelihood,
        impact=risk.impact,
    )

    risk.inherent_level = crud.calculate_risk_level(
        risk.inherent_score
    )

    if (
        risk.residual_likelihood is not None
        and risk.residual_impact is not None
    ):
        risk.residual_score = crud.calculate_risk_score(
            risk.residual_likelihood,
            risk.residual_impact,
        )

        risk.residual_level = crud.calculate_risk_level(
            risk.residual_score
        )
    else:
        risk.residual_score = None
        risk.residual_level = None

    db.commit()
    db.refresh(risk)

    return risk



# =========================================================
# ISO Controls
# =========================================================

@app.get(
    "/controls",
    response_model=list[schemas.ControlResponse],
    tags=["ISO Controls"],
)
def list_controls(
    db: DatabaseSession,
):
    return crud.get_controls(db)


@app.get(
    "/controls/{control_id}",
    response_model=schemas.ControlResponse,
    tags=["ISO Controls"],
)
def read_control(
    control_id: int,
    db: DatabaseSession,
):
    control = crud.get_control(db, control_id)

    if control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found.",
        )

    return control


@app.post(
    "/controls",
    response_model=schemas.ControlResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["ISO Controls"],
)
def create_control(
    control_data: schemas.ControlCreate,
    db: DatabaseSession,
):
    existing_control = crud.get_control_by_code(
        db,
        control_data.control_code,
    )

    if existing_control:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Control code already exists.",
        )

    try:
        return crud.create_control(db, control_data)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create control.",
        )


@app.put(
    "/controls/{control_id}",
    response_model=schemas.ControlResponse,
    tags=["ISO Controls"],
)
def update_control(
    control_id: int,
    control_data: schemas.ControlUpdate,
    db: DatabaseSession,
):
    control = crud.get_control(db, control_id)

    if control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found.",
        )

    update_values = control_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_values.items():
        setattr(control, field, value)

    db.commit()
    db.refresh(control)

    return control



# =========================================================
# Risk-Control Mappings
# =========================================================

@app.get(
    "/risk-controls",
    response_model=list[schemas.RiskControlResponse],
    tags=["Risk-Control Mapping"],
)
def list_risk_control_mappings(
    db: DatabaseSession,
):
    return crud.get_risk_control_mappings(db)


@app.get(
    "/risk-controls/{mapping_id}",
    response_model=schemas.RiskControlResponse,
    tags=["Risk-Control Mapping"],
)
def read_risk_control_mapping(
    mapping_id: int,
    db: DatabaseSession,
):
    mapping = crud.get_risk_control_mapping(
        db,
        mapping_id,
    )

    if mapping is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk-control mapping not found.",
        )

    return mapping


@app.get(
    "/risks/{risk_id}/controls",
    response_model=list[schemas.RiskControlResponse],
    tags=["Risk-Control Mapping"],
)
def list_controls_for_risk(
    risk_id: int,
    db: DatabaseSession,
):
    risk = crud.get_risk_assessment(db, risk_id)

    if risk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found.",
        )

    return crud.get_control_mappings_for_risk(
        db,
        risk_id,
    )


@app.post(
    "/risk-controls",
    response_model=schemas.RiskControlResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Risk-Control Mapping"],
)
def create_risk_control_mapping(
    mapping_data: schemas.RiskControlCreate,
    db: DatabaseSession,
):
    risk = crud.get_risk_assessment(
        db,
        mapping_data.risk_id,
    )

    if risk is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected risk assessment does not exist.",
        )

    control = crud.get_control(
        db,
        mapping_data.control_id,
    )

    if control is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected control does not exist.",
        )

    existing_mapping = (
        crud.get_mapping_by_risk_and_control(
            db,
            mapping_data.risk_id,
            mapping_data.control_id,
        )
    )

    if existing_mapping:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This control is already mapped "
                "to the selected risk."
            ),
        )

    try:
        return crud.create_risk_control_mapping(
            db,
            mapping_data,
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create risk-control mapping.",
        )


@app.put(
    "/risk-controls/{mapping_id}",
    response_model=schemas.RiskControlResponse,
    tags=["Risk-Control Mapping"],
)
def update_risk_control_mapping(
    mapping_id: int,
    mapping_data: schemas.RiskControlUpdate,
    db: DatabaseSession,
):
    mapping = crud.get_risk_control_mapping(
        db,
        mapping_id,
    )

    if mapping is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk-control mapping not found.",
        )

    return crud.update_risk_control_mapping(
        db,
        mapping,
        mapping_data,
    )


@app.delete(
    "/risk-controls/{mapping_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Risk-Control Mapping"],
)
def delete_risk_control_mapping(
    mapping_id: int,
    db: DatabaseSession,
):
    mapping = crud.get_risk_control_mapping(
        db,
        mapping_id,
    )

    if mapping is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk-control mapping not found.",
        )

    crud.delete_risk_control_mapping(
        db,
        mapping,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )




# =========================================================
# Compliance Dashboard
# =========================================================

@app.get(
    "/compliance/summary",
    response_model=schemas.ComplianceSummaryResponse,
    tags=["Compliance Dashboard"],
)
def compliance_summary(
    db: DatabaseSession,
):
    return crud.get_compliance_summary(db)

@app.get(
    "/compliance/overdue-controls",
    response_model=list[schemas.OverdueControlResponse],
    tags=["Compliance Dashboard"],
)
def overdue_controls(
    db: DatabaseSession,
):
    return crud.get_overdue_controls(db)

@app.get(
    "/compliance/dashboard",
    response_model=schemas.ComplianceDashboardResponse,
    tags=["Compliance Dashboard"],
)
def compliance_dashboard(
    db: DatabaseSession,
):
    return crud.get_compliance_dashboard(db)