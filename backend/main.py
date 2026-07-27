from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

import models
from database import Base, engine

app = FastAPI(
    title="Cyber_X_Force API",
    description=(
        "ISO/IEC 27001-based Governance, Risk and Compliance API "
        "for AutoSecure Manufacturing GmbH."
    ),
    version="0.1.0",
)


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "application": "Cyber_X_Force",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }

    except SQLAlchemyError:
        return {
            "status": "unhealthy",
            "database": "disconnected",
        }