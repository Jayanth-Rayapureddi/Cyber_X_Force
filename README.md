# Cyber_X_Force

Cyber_X_Force is an ISO/IEC 27001-aligned cybersecurity Governance, Risk and Compliance platform developed as an academic cybersecurity project.

The platform supports information-asset management, risk assessment, ISO control implementation, compliance monitoring, audit management, evidence handling, corrective actions, incident management, authentication, role-based access control, audit logging, dashboards and executive reporting.

---

## Project Objectives

The main objectives of Cyber_X_Force are to:

- Implement a practical cybersecurity risk-management platform.
- Demonstrate ISO/IEC 27001 control and compliance management.
- Maintain information assets, risks, incidents and audit records.
- Track corrective actions and supporting evidence.
- Enforce authentication and role-based access control.
- Provide management dashboards and downloadable reports.
- Maintain an audit trail of important user and API activity.

---

## Core Features

### Authentication and Security

- JWT-based authentication
- Secure password hashing
- Login and logout
- User activation and deactivation
- Password reset
- Role-based access control
- Protected frontend pages
- API audit logging

### Asset Management

- Register information assets
- Assign owners and departments
- Record confidentiality, integrity and availability ratings
- Calculate asset criticality
- Maintain active and inactive asset status

### Risk Management

- Create and manage risk assessments
- Link assets, threats and vulnerabilities
- Record likelihood and impact
- Calculate inherent risk scores
- Record treatment options
- Track residual risk
- Display risk-level analytics

### ISO/IEC 27001 Controls

- Maintain an ISO control library
- Organize controls by category
- Record implementation status
- Track implementation percentage
- Assign control owners
- Set target dates
- Identify overdue controls

### Compliance Management

- Calculate compliance percentage
- Display control-status distribution
- Show average implementation progress
- Track overdue controls
- Record compliance assessments

### Evidence Repository

- Upload evidence files
- Store evidence metadata
- Link evidence to controls and assessments
- Verify evidence
- Download evidence
- Delete evidence
- Monitor evidence-storage status

### Audits and Findings

- Create internal and external audits
- Record audit scope and schedule
- Assign lead auditors
- Record audit findings
- Categorize findings
- Assign severity and ownership
- Track due dates and finding status

### Corrective Actions

- Link corrective actions to findings
- Assign action owners
- Track completion percentage
- Set target and completion dates
- Record verification results
- Monitor remediation progress

### Incident Management

- Record cybersecurity incidents
- Assign severity and category
- Link affected assets
- Assign incident owners
- Track investigation and closure
- Record containment, root cause and lessons learned

### Dashboards and Reporting

- Executive management dashboard
- Risk profile analytics
- Compliance-readiness gauge
- Control-status visualization
- Operational workload chart
- Critical-risk monitoring
- Recent incidents and findings
- Upcoming audits
- Latest evidence
- PDF report generation
- Excel management workbook
- Audit Trail dashboard
- CSV export

### User Administration

- View users
- Create users
- Edit user details
- Assign roles
- Assign departments
- Enable and disable users
- Reset passwords
- Search and filter users

---

## User Roles

The application includes the following roles:

| Role | Main Access |
|---|---|
| Administrator | Full system access |
| Risk Analyst | Assets, risks, controls and compliance |
| Asset Owner | Assets, risks, controls and evidence |
| Internal Auditor | Controls, compliance, evidence, audits and reports |
| Incident Manager | Incidents, risks, corrective actions and evidence |
| Executive Viewer | Read-only dashboard, compliance, system status and reports |

---

## Technology Stack

### Frontend

- Streamlit
- Pandas
- Plotly
- OpenPyXL
- ReportLab

### Backend

- FastAPI
- SQLAlchemy
- Pydantic
- JWT authentication
- Password hashing

### Database

- PostgreSQL 17

### Infrastructure

- Docker
- Docker Compose

---

## Project Structure

```text
Cyber_X_Force/
│
├── backend/
│   ├── crud.py
│   ├── database.py
│   ├── Dockerfile
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── schemas.py
│   └── seed.py
│
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/
├── docs/
├── uploads/
│   └── evidence/
│
├── .env
├── .env.example
├── docker-compose.yml
└── README.md

Cyber_X_Force is a full-stack cybersecurity Governance, Risk and Compliance (GRC) platform developed as an academic project.

## Table of Contents

1. Project Overview
2. Objectives
3. Features
4. Technology Stack
5. Project Structure
6. Installation
7. Environment Configuration
8. Running the Application
9. Application URLs
10. Demo Accounts
11. User Roles
12. Main Modules
13. API Overview
14. Reports Center
15. Audit Trail
16. Testing
17. Demonstration Workflow
18. ISO/IEC 27001 Alignment
19. Security Considerations
20. Limitations
21. Future Improvements
22. Troubleshooting
23. Team
24. License

---

## Project Overview

Cyber_X_Force provides:
- Authentication
- RBAC
- Asset Management
- Risk Register
- ISO Controls
- Compliance
- Evidence
- Audits
- Findings
- Corrective Actions
- Incidents
- Executive Dashboard
- Reports Center
- Audit Trail

## Technology Stack

Frontend:
- Streamlit
- Plotly
- Pandas
- ReportLab

Backend:
- FastAPI
- SQLAlchemy
- Pydantic

Database:
- PostgreSQL 17

Infrastructure:
- Docker
- Docker Compose

## Installation

```bash
git clone https://github.com/Jayanth-Rayapureddi/Cyber_X_Force.git
cd Cyber_X_Force
docker compose up -d --build
```

## URLs

- Frontend: http://localhost:8501
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Demo Accounts

- admin@cyberxforce.com
- risk@cyberxforce.com
- auditor@cyberxforce.com
- asset@cyberxforce.com
- incident@cyberxforce.com
- executive@cyberxforce.com

## Modules

- Dashboard
- Assets
- Risks
- ISO Controls
- Compliance
- Evidence
- Audits
- Audit Findings
- Corrective Actions
- Incidents
- User Administration
- Audit Trail
- Reports Center

## Reports

- Executive PDF
- Risk Register
- Compliance
- Audit
- Incident
- Corrective Actions
- Excel Workbook

## Testing

- Authentication
- RBAC
- CRUD
- Evidence Upload
- Reports
- Dashboard
- Audit Trail

## ISO 27001 Alignment

- Assets
- Risks
- Controls
- Compliance
- Audits
- Evidence
- Corrective Actions
- Incident Management

## Future Improvements

- MFA
- Keycloak
- Notifications
- SIEM Integration
- Risk Heatmaps

## Team

- Jayanth Rayapureddi
- Ramakrishna Vamsi Kolapalli
- Deepsika Nimmagadda

## License

Academic and demonstration purposes only.
