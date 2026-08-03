from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated
import os
from datetime import timedelta
from pathlib import Path
from uuid import uuid4


from fastapi import Depends, FastAPI, HTTPException, Response, status, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.responses import FileResponse
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import Base, SessionLocal, engine, get_db
from seed import seed_initial_data


DatabaseSession = Annotated[Session, Depends(get_db)]

EVIDENCE_UPLOAD_DIR = Path("/uploads/evidence")
EVIDENCE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EVIDENCE_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".xls", ".png", ".jpg", ".jpeg", ".txt", ".csv"}
MAX_EVIDENCE_FILE_SIZE = 10 * 1024 * 1024


SECRET_KEY = os.getenv("SECRET_KEY", "change-this-development-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
PASSWORD_CONTEXT = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

PUBLIC_PATHS = {"/", "/health", "/auth/login", "/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}
ROLE_WRITE_PREFIXES = {
    "Administrator": ("/",),
    "Risk Manager": ("/assets", "/risks", "/controls", "/risk-controls", "/threats", "/vulnerabilities"),
    "Asset Owner": ("/assets",),
    "Internal Auditor": ("/audits", "/audit-findings", "/evidence", "/compliance-assessments"),
    "Incident Manager": ("/incidents", "/incident-actions", "/corrective-actions"),
    "Executive Viewer": tuple(),
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PASSWORD_CONTEXT.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return PASSWORD_CONTEXT.hash(password)

def create_access_token(user: models.User, role_name: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user.id), "email": user.email, "role": role_name, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token.") from exc


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


@app.middleware("http")
async def authentication_and_audit_middleware(request: Request, call_next):
    path = request.url.path
    if path in PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
        return await call_next(request)

    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Authentication required."})

    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub", 0))
    except (HTTPException, ValueError, TypeError):
        return JSONResponse(status_code=401, content={"detail": "Invalid or expired access token."})

    with SessionLocal() as auth_db:
        user = auth_db.get(models.User, user_id)
        if user is None or not user.is_active:
            return JSONResponse(status_code=401, content={"detail": "User account is inactive or unavailable."})
        role = auth_db.get(models.Role, user.role_id)
        role_name = role.name if role else "Unknown"

    request.state.user_id = user.id
    request.state.user_email = user.email
    request.state.role_name = role_name

    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        prefixes = ROLE_WRITE_PREFIXES.get(role_name, tuple())
        if role_name != "Administrator" and not any(path.startswith(prefix) for prefix in prefixes):
            return JSONResponse(status_code=403, content={"detail": f"Role '{role_name}' cannot modify this resource."})

    response = await call_next(request)

    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        try:
            with SessionLocal() as audit_db:
                crud.create_audit_log(
                    audit_db, user_id=user.id, user_email=user.email,
                    action=f"{request.method} request", resource=path, method=request.method,
                    status_code=response.status_code,
                    ip_address=request.client.host if request.client else None,
                )
        except Exception:
            pass
    return response


def current_user_from_request(request: Request, db: Session) -> tuple[models.User, models.Role]:
    user = db.get(models.User, getattr(request.state, "user_id", 0))
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required.")
    role = db.get(models.Role, user.role_id)
    if role is None:
        raise HTTPException(status_code=403, detail="User role is unavailable.")
    return user, role

@app.post("/auth/login", response_model=schemas.TokenResponse, tags=["Authentication"])
def login(login_data: schemas.LoginRequest, request: Request, db: DatabaseSession):
    user = crud.get_user_by_email(db, str(login_data.email))
    if user is None or not user.is_active or not verify_password(login_data.password, user.hashed_password):
        try:
            crud.create_audit_log(db, user_id=user.id if user else None, user_email=str(login_data.email), action="Login failed", resource="/auth/login", method="POST", status_code=401, ip_address=request.client.host if request.client else None)
        except Exception:
            pass
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    role = db.get(models.Role, user.role_id)
    token = create_access_token(user, role.name if role else "Unknown")
    crud.create_audit_log(db, user_id=user.id, user_email=user.email, action="Login successful", resource="/auth/login", method="POST", status_code=200, ip_address=request.client.host if request.client else None)
    return {
        "access_token": token, "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {"id": user.id, "full_name": user.full_name, "email": user.email, "role_id": user.role_id, "role_name": role.name if role else "Unknown", "department_id": user.department_id, "is_active": user.is_active},
    }

@app.get("/auth/me", response_model=schemas.CurrentUserResponse, tags=["Authentication"])
def auth_me(request: Request, db: DatabaseSession):
    user, role = current_user_from_request(request, db)
    return {"id": user.id, "full_name": user.full_name, "email": user.email, "role_id": user.role_id, "role_name": role.name, "department_id": user.department_id, "is_active": user.is_active}

@app.get("/users", response_model=list[schemas.UserResponse], tags=["User Administration"])
def list_users(request: Request, db: DatabaseSession):
    _, role = current_user_from_request(request, db)
    if role.name != "Administrator":
        raise HTTPException(status_code=403, detail="Administrator access required.")
    return crud.get_users(db)

@app.post("/users", response_model=schemas.UserResponse, status_code=201, tags=["User Administration"])
def create_user(user_data: schemas.UserCreate, request: Request, db: DatabaseSession):
    _, role = current_user_from_request(request, db)
    if role.name != "Administrator":
        raise HTTPException(status_code=403, detail="Administrator access required.")
    if crud.get_user_by_email(db, str(user_data.email)):
        raise HTTPException(status_code=409, detail="Email address already exists.")
    if db.get(models.Role, user_data.role_id) is None:
        raise HTTPException(status_code=400, detail="Selected role does not exist.")
    return crud.create_user_record(db, user_data, hash_password(user_data.password))

@app.put("/users/{user_id}", response_model=schemas.UserResponse, tags=["User Administration"])
def update_user(user_id: int, user_data: schemas.UserUpdate, request: Request, db: DatabaseSession):
    _, role = current_user_from_request(request, db)
    if role.name != "Administrator":
        raise HTTPException(status_code=403, detail="Administrator access required.")
    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    values = user_data.model_dump(exclude_unset=True)

    new_email = values.get("email")
    if new_email:
        existing_user = crud.get_user_by_email(db, str(new_email))
        if existing_user is not None and existing_user.id != user.id:
            raise HTTPException(status_code=409, detail="Email address already exists.")
        values["email"] = str(new_email).lower()

    if values.get("role_id") is not None and db.get(models.Role, values["role_id"]) is None:
        raise HTTPException(status_code=400, detail="Selected role does not exist.")

    if values.get("department_id") is not None and db.get(models.Department, values["department_id"]) is None:
        raise HTTPException(status_code=400, detail="Selected department does not exist.")

    current_admin, _ = current_user_from_request(request, db)
    if user.id == current_admin.id and values.get("is_active") is False:
        raise HTTPException(status_code=400, detail="You cannot disable your own account.")

    password = values.pop("password", None)
    if password:
        values["hashed_password"] = hash_password(password)

    return crud.update_user_record(db, user, values)

@app.get("/audit-logs", response_model=list[schemas.AuditLogResponse], tags=["Audit Trail"])
def list_audit_logs(request: Request, db: DatabaseSession, limit: int = 200):
    _, role = current_user_from_request(request, db)
    if role.name not in {"Administrator", "Internal Auditor"}:
        raise HTTPException(status_code=403, detail="Administrator or Internal Auditor access required.")
    return crud.get_audit_logs(db, min(max(limit, 1), 1000))


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

# =========================================================
# Compliance Assessments
# =========================================================

@app.get("/compliance-assessments", response_model=list[schemas.ComplianceAssessmentResponse], tags=["Compliance Assessments"])
def list_compliance_assessments(db: DatabaseSession): return crud.get_compliance_assessments(db)

@app.get("/compliance-assessments/{assessment_id}", response_model=schemas.ComplianceAssessmentResponse, tags=["Compliance Assessments"])
def read_compliance_assessment(assessment_id: int, db: DatabaseSession):
    obj=crud.get_compliance_assessment(db, assessment_id)
    if obj is None: raise HTTPException(status_code=404, detail="Compliance assessment not found.")
    return obj

@app.post("/compliance-assessments", response_model=schemas.ComplianceAssessmentResponse, status_code=201, tags=["Compliance Assessments"])
def create_compliance_assessment(data: schemas.ComplianceAssessmentCreate, db: DatabaseSession):
    if crud.get_compliance_assessment_by_code(db, data.assessment_code): raise HTTPException(status_code=409, detail="Assessment code already exists.")
    if crud.get_control(db, data.control_id) is None: raise HTTPException(status_code=400, detail="Selected control does not exist.")
    return crud.create_compliance_assessment(db, data)

@app.put("/compliance-assessments/{assessment_id}", response_model=schemas.ComplianceAssessmentResponse, tags=["Compliance Assessments"])
def update_compliance_assessment(assessment_id: int, data: schemas.ComplianceAssessmentUpdate, db: DatabaseSession):
    obj=crud.get_compliance_assessment(db, assessment_id)
    if obj is None: raise HTTPException(status_code=404, detail="Compliance assessment not found.")
    return crud.update_compliance_assessment(db, obj, data)

@app.delete("/compliance-assessments/{assessment_id}", status_code=204, tags=["Compliance Assessments"])
def delete_compliance_assessment(assessment_id: int, db: DatabaseSession):
    obj=crud.get_compliance_assessment(db, assessment_id)
    if obj is None: raise HTTPException(status_code=404, detail="Compliance assessment not found.")
    crud.delete_compliance_assessment(db, obj); return Response(status_code=204)


# =========================================================
# Evidence
# =========================================================

@app.get("/evidence", response_model=list[schemas.EvidenceResponse], tags=["Evidence"])
def list_evidence(db: DatabaseSession):
    return crud.get_evidence_records(db)

@app.post("/evidence/upload", response_model=schemas.EvidenceResponse, status_code=status.HTTP_201_CREATED, tags=["Evidence"])
async def upload_evidence(
    db: DatabaseSession,
    evidence_code: str = Form(...),
    title: str = Form(...),
    evidence_type: str = Form(...),
    collected_at: str = Form(...),
    file: UploadFile = File(...),
    description: str | None = Form(None),
    control_id: int | None = Form(None),
    assessment_id: int | None = Form(None),
    owner: str | None = Form(None),
    valid_until: str | None = Form(None),
    is_verified: bool = Form(False),
    verification_notes: str | None = Form(None),
):
    if crud.get_evidence_by_code(db, evidence_code):
        raise HTTPException(status_code=409, detail="Evidence code already exists.")
    if control_id is not None and crud.get_control(db, control_id) is None:
        raise HTTPException(status_code=400, detail="Selected control does not exist.")
    if assessment_id is not None and crud.get_compliance_assessment(db, assessment_id) is None:
        raise HTTPException(status_code=400, detail="Selected assessment does not exist.")

    original_name = Path(file.filename or "evidence").name
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EVIDENCE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: PDF, DOCX, XLS/XLSX, PNG/JPG, TXT and CSV.")

    stored_name = f"{uuid4().hex}{extension}"
    destination = EVIDENCE_UPLOAD_DIR / stored_name
    written = 0
    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                written += len(chunk)
                if written > MAX_EVIDENCE_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="File exceeds the 10 MB limit.")
                output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    try:
        data = schemas.EvidenceCreate(
            evidence_code=evidence_code,
            title=title,
            evidence_type=evidence_type,
            description=description,
            reference_location=f"/uploads/evidence/{stored_name}",
            control_id=control_id,
            assessment_id=assessment_id,
            owner=owner,
            collected_at=collected_at,
            valid_until=valid_until or None,
            is_verified=is_verified,
            verification_notes=(f"Original file: {original_name}; Size: {written} bytes" + (f"; {verification_notes}" if verification_notes else "")),
        )
        return crud.create_evidence(db, data)
    except Exception:
        destination.unlink(missing_ok=True)
        raise

@app.get("/evidence/{evidence_id}/download", tags=["Evidence"])
def download_evidence(evidence_id: int, db: DatabaseSession):
    obj = crud.get_evidence(db, evidence_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    path = EVIDENCE_UPLOAD_DIR / Path(obj.reference_location).name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Uploaded evidence file not found.")
    original_name = obj.title + path.suffix
    if obj.verification_notes and "Original file:" in obj.verification_notes:
        original_name = obj.verification_notes.split("Original file:", 1)[1].split(";", 1)[0].strip()
    return FileResponse(path=path, filename=original_name, media_type="application/octet-stream")

@app.get("/evidence/{evidence_id}", response_model=schemas.EvidenceResponse, tags=["Evidence"])
def read_evidence(evidence_id: int, db: DatabaseSession):
    obj = crud.get_evidence(db, evidence_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    return obj

@app.post("/evidence", response_model=schemas.EvidenceResponse, status_code=201, tags=["Evidence"])
def create_evidence(data: schemas.EvidenceCreate, db: DatabaseSession):
    if crud.get_evidence_by_code(db, data.evidence_code):
        raise HTTPException(status_code=409, detail="Evidence code already exists.")
    if data.control_id is not None and crud.get_control(db, data.control_id) is None:
        raise HTTPException(status_code=400, detail="Selected control does not exist.")
    if data.assessment_id is not None and crud.get_compliance_assessment(db, data.assessment_id) is None:
        raise HTTPException(status_code=400, detail="Selected assessment does not exist.")
    return crud.create_evidence(db, data)

@app.put("/evidence/{evidence_id}", response_model=schemas.EvidenceResponse, tags=["Evidence"])
def update_evidence(evidence_id: int, data: schemas.EvidenceUpdate, db: DatabaseSession):
    obj = crud.get_evidence(db, evidence_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    return crud.update_evidence(db, obj, data)

@app.delete("/evidence/{evidence_id}", status_code=204, tags=["Evidence"])
def delete_evidence(evidence_id: int, db: DatabaseSession):
    obj = crud.get_evidence(db, evidence_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    path = EVIDENCE_UPLOAD_DIR / Path(obj.reference_location).name
    crud.delete_evidence(db, obj)
    path.unlink(missing_ok=True)
    return Response(status_code=204)


# =========================================================
# Audits and Findings
# =========================================================

@app.get("/audits", response_model=list[schemas.AuditResponse], tags=["Audits"])
def list_audits(db: DatabaseSession): return crud.get_audits(db)
@app.get("/audits/{audit_id}", response_model=schemas.AuditResponse, tags=["Audits"])
def read_audit(audit_id: int, db: DatabaseSession):
    obj=crud.get_audit(db,audit_id)
    if obj is None: raise HTTPException(status_code=404, detail="Audit not found.")
    return obj
@app.post("/audits", response_model=schemas.AuditResponse, status_code=201, tags=["Audits"])
def create_audit(data: schemas.AuditCreate, db: DatabaseSession):
    if crud.get_audit_by_code(db,data.audit_code): raise HTTPException(status_code=409, detail="Audit code already exists.")
    if data.planned_end_date < data.planned_start_date: raise HTTPException(status_code=400, detail="Audit end date cannot be before start date.")
    return crud.create_audit(db,data)
@app.put("/audits/{audit_id}", response_model=schemas.AuditResponse, tags=["Audits"])
def update_audit(audit_id:int,data:schemas.AuditUpdate,db:DatabaseSession):
    obj=crud.get_audit(db,audit_id)
    if obj is None: raise HTTPException(status_code=404,detail="Audit not found.")
    return crud.update_audit(db,obj,data)
@app.delete("/audits/{audit_id}",status_code=204,tags=["Audits"])
def delete_audit(audit_id:int,db:DatabaseSession):
    obj=crud.get_audit(db,audit_id)
    if obj is None: raise HTTPException(status_code=404,detail="Audit not found.")
    crud.delete_audit(db,obj); return Response(status_code=204)

@app.get("/audit-findings",response_model=list[schemas.AuditFindingResponse],tags=["Audit Findings"])
def list_audit_findings(db:DatabaseSession): return crud.get_audit_findings(db)
@app.post("/audit-findings",response_model=schemas.AuditFindingResponse,status_code=201,tags=["Audit Findings"])
def create_audit_finding(data:schemas.AuditFindingCreate,db:DatabaseSession):
    if crud.get_finding_by_code(db,data.finding_code): raise HTTPException(status_code=409,detail="Finding code already exists.")
    if crud.get_audit(db,data.audit_id) is None: raise HTTPException(status_code=400,detail="Selected audit does not exist.")
    if data.control_id is not None and crud.get_control(db,data.control_id) is None: raise HTTPException(status_code=400,detail="Selected control does not exist.")
    return crud.create_audit_finding(db,data)
@app.get("/audit-findings/{finding_id}",response_model=schemas.AuditFindingResponse,tags=["Audit Findings"])
def read_audit_finding(finding_id:int,db:DatabaseSession):
    obj=crud.get_audit_finding(db,finding_id)
    if obj is None: raise HTTPException(status_code=404,detail="Audit finding not found.")
    return obj
@app.put("/audit-findings/{finding_id}",response_model=schemas.AuditFindingResponse,tags=["Audit Findings"])
def update_audit_finding(finding_id:int,data:schemas.AuditFindingUpdate,db:DatabaseSession):
    obj=crud.get_audit_finding(db,finding_id)
    if obj is None: raise HTTPException(status_code=404,detail="Audit finding not found.")
    return crud.update_audit_finding(db,obj,data)
@app.delete("/audit-findings/{finding_id}",status_code=204,tags=["Audit Findings"])
def delete_audit_finding(finding_id:int,db:DatabaseSession):
    obj=crud.get_audit_finding(db,finding_id)
    if obj is None: raise HTTPException(status_code=404,detail="Audit finding not found.")
    crud.delete_audit_finding(db,obj); return Response(status_code=204)


# =========================================================
# Corrective Actions
# =========================================================

@app.get("/corrective-actions",response_model=list[schemas.CorrectiveActionResponse],tags=["Corrective Actions"])
def list_corrective_actions(db:DatabaseSession): return crud.get_corrective_actions(db)
@app.post("/corrective-actions",response_model=schemas.CorrectiveActionResponse,status_code=201,tags=["Corrective Actions"])
def create_corrective_action(data:schemas.CorrectiveActionCreate,db:DatabaseSession):
    if crud.get_corrective_action_by_code(db,data.action_code): raise HTTPException(status_code=409,detail="Action code already exists.")
    if crud.get_audit_finding(db,data.finding_id) is None: raise HTTPException(status_code=400,detail="Selected audit finding does not exist.")
    return crud.create_corrective_action(db,data)
@app.get("/corrective-actions/{action_id}",response_model=schemas.CorrectiveActionResponse,tags=["Corrective Actions"])
def read_corrective_action(action_id:int,db:DatabaseSession):
    obj=crud.get_corrective_action(db,action_id)
    if obj is None: raise HTTPException(status_code=404,detail="Corrective action not found.")
    return obj
@app.put("/corrective-actions/{action_id}",response_model=schemas.CorrectiveActionResponse,tags=["Corrective Actions"])
def update_corrective_action(action_id:int,data:schemas.CorrectiveActionUpdate,db:DatabaseSession):
    obj=crud.get_corrective_action(db,action_id)
    if obj is None: raise HTTPException(status_code=404,detail="Corrective action not found.")
    return crud.update_corrective_action(db,obj,data)
@app.delete("/corrective-actions/{action_id}",status_code=204,tags=["Corrective Actions"])
def delete_corrective_action(action_id:int,db:DatabaseSession):
    obj=crud.get_corrective_action(db,action_id)
    if obj is None: raise HTTPException(status_code=404,detail="Corrective action not found.")
    crud.delete_corrective_action(db,obj); return Response(status_code=204)


# =========================================================
# Incidents
# =========================================================

@app.get("/incidents",response_model=list[schemas.IncidentResponse],tags=["Incidents"])
def list_incidents(db:DatabaseSession): return crud.get_incidents(db)
@app.post("/incidents",response_model=schemas.IncidentResponse,status_code=201,tags=["Incidents"])
def create_incident(data:schemas.IncidentCreate,db:DatabaseSession):
    if crud.get_incident_by_code(db,data.incident_code): raise HTTPException(status_code=409,detail="Incident code already exists.")
    if data.asset_id is not None and crud.get_asset(db,data.asset_id) is None: raise HTTPException(status_code=400,detail="Selected asset does not exist.")
    return crud.create_incident(db,data)
@app.get("/incidents/{incident_id}",response_model=schemas.IncidentResponse,tags=["Incidents"])
def read_incident(incident_id:int,db:DatabaseSession):
    obj=crud.get_incident(db,incident_id)
    if obj is None: raise HTTPException(status_code=404,detail="Incident not found.")
    return obj
@app.put("/incidents/{incident_id}",response_model=schemas.IncidentResponse,tags=["Incidents"])
def update_incident(incident_id:int,data:schemas.IncidentUpdate,db:DatabaseSession):
    obj=crud.get_incident(db,incident_id)
    if obj is None: raise HTTPException(status_code=404,detail="Incident not found.")
    return crud.update_incident(db,obj,data)
@app.delete("/incidents/{incident_id}",status_code=204,tags=["Incidents"])
def delete_incident(incident_id:int,db:DatabaseSession):
    obj=crud.get_incident(db,incident_id)
    if obj is None: raise HTTPException(status_code=404,detail="Incident not found.")
    crud.delete_incident(db,obj); return Response(status_code=204)
@app.get("/incidents/{incident_id}/actions",response_model=list[schemas.IncidentActionResponse],tags=["Incidents"])
def list_incident_actions(incident_id:int,db:DatabaseSession):
    if crud.get_incident(db,incident_id) is None: raise HTTPException(status_code=404,detail="Incident not found.")
    return crud.get_incident_actions(db,incident_id)
@app.post("/incident-actions",response_model=schemas.IncidentActionResponse,status_code=201,tags=["Incidents"])
def create_incident_action(data:schemas.IncidentActionCreate,db:DatabaseSession):
    if crud.get_incident(db,data.incident_id) is None: raise HTTPException(status_code=400,detail="Selected incident does not exist.")
    return crud.create_incident_action(db,data)




@app.get("/management/system-status", tags=["Management Dashboard"])
def management_system_status(db: DatabaseSession) -> dict[str, object]:
    """Return operational health, database record counts and evidence-storage metrics."""
    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"
    except SQLAlchemyError:
        database_status = "disconnected"

    model_counts = {
        "assets": models.Asset,
        "risks": models.RiskAssessment,
        "controls": models.Control,
        "evidence": models.Evidence,
        "audits": models.Audit,
        "findings": models.AuditFinding,
        "corrective_actions": models.CorrectiveAction,
        "incidents": models.Incident,
    }

    record_counts = {
        name: int(
            db.scalar(
                select(func.count()).select_from(model)
            )
            or 0
        )
        for name, model in model_counts.items()
    }

    upload_folder_exists = EVIDENCE_UPLOAD_DIR.exists()
    evidence_files = [
        path
        for path in EVIDENCE_UPLOAD_DIR.iterdir()
        if path.is_file()
    ] if upload_folder_exists else []

    storage_bytes = sum(
        path.stat().st_size
        for path in evidence_files
    )

    return {
        "application": "Cyber_X_Force",
        "backend_status": "healthy",
        "database_status": database_status,
        "version": app.version,
        "server_time_utc": datetime.now(timezone.utc).isoformat(),
        "record_counts": record_counts,
        "storage": {
            "upload_folder": str(EVIDENCE_UPLOAD_DIR),
            "upload_folder_exists": upload_folder_exists,
            "upload_folder_writable": (
                upload_folder_exists
                and EVIDENCE_UPLOAD_DIR.is_dir()
            ),
            "stored_files": len(evidence_files),
            "storage_bytes": storage_bytes,
        },
        "checks": {
            "api_responding": True,
            "database_responding": database_status == "connected",
            "upload_folder_accessible": upload_folder_exists,
            "iso_controls_loaded": record_counts["controls"] > 0,
            "assets_loaded": record_counts["assets"] > 0,
            "risks_loaded": record_counts["risks"] > 0,
        },
    }


@app.get("/management/dashboard",response_model=schemas.ManagementDashboardResponse,tags=["Management Dashboard"])
def management_dashboard(db:DatabaseSession): return crud.get_management_dashboard(db)
