from sqlalchemy import select
from sqlalchemy.orm import Session

import models


DEFAULT_ROLES = [
    {
        "name": "Administrator",
        "description": "Full system administration access.",
    },
    {
        "name": "Risk Manager",
        "description": "Manages risks and treatment plans.",
    },
    {
        "name": "Asset Owner",
        "description": "Manages assigned information assets.",
    },
    {
        "name": "Incident Manager",
        "description": "Manages cybersecurity incidents.",
    },
    {
        "name": "Internal Auditor",
        "description": "Performs audits and verifies evidence.",
    },
    {
        "name": "Executive Viewer",
        "description": "Views management dashboards and reports.",
    },
]


DEFAULT_DEPARTMENTS = [
    {
        "name": "Executive Management",
        "location": "Berlin Headquarters",
    },
    {
        "name": "Human Resources",
        "location": "Berlin Headquarters",
    },
    {
        "name": "Finance and Accounting",
        "location": "Berlin Headquarters",
    },
    {
        "name": "Information Technology",
        "location": "Berlin Headquarters",
    },
    {
        "name": "Cybersecurity",
        "location": "Berlin Headquarters",
    },
    {
        "name": "Research and Development",
        "location": "Berlin Headquarters",
    },
    {
        "name": "Manufacturing",
        "location": "Leipzig Factory",
    },
    {
        "name": "Quality Assurance",
        "location": "Leipzig Factory",
    },
    {
        "name": "Procurement",
        "location": "Berlin Headquarters",
    },
    {
        "name": "Sales and Marketing",
        "location": "Berlin Headquarters",
    },
    {
        "name": "Logistics",
        "location": "Hamburg Logistics Centre",
    },
    {
        "name": "Customer Support",
        "location": "Berlin Headquarters",
    },
]


DEFAULT_THREATS = [
    {
        "threat_code": "THR-001",
        "name": "Ransomware",
        "category": "Malware",
        "description": (
            "Malicious software encrypts organisational data "
            "and demands payment for recovery."
        ),
        "source": "External Threat Actor",
        "default_likelihood": 4,
    },
    {
        "threat_code": "THR-002",
        "name": "Phishing",
        "category": "Social Engineering",
        "description": (
            "Fraudulent messages attempt to steal credentials "
            "or persuade employees to execute malicious content."
        ),
        "source": "External Threat Actor",
        "default_likelihood": 5,
    },
    {
        "threat_code": "THR-003",
        "name": "Insider Threat",
        "category": "Human Threat",
        "description": (
            "An employee or contractor intentionally or "
            "accidentally compromises information security."
        ),
        "source": "Internal",
        "default_likelihood": 3,
    },
    {
        "threat_code": "THR-004",
        "name": "Distributed Denial of Service",
        "category": "Network Attack",
        "description": (
            "A large volume of malicious traffic disrupts "
            "the availability of systems or services."
        ),
        "source": "External Threat Actor",
        "default_likelihood": 3,
    },
    {
        "threat_code": "THR-005",
        "name": "Credential Theft",
        "category": "Identity Attack",
        "description": (
            "Account credentials are stolen and used to gain "
            "unauthorised access."
        ),
        "source": "External Threat Actor",
        "default_likelihood": 4,
    },
    {
        "threat_code": "THR-006",
        "name": "Supply Chain Compromise",
        "category": "Third-Party Threat",
        "description": (
            "A supplier or third-party system is compromised "
            "and used to attack the organisation."
        ),
        "source": "Third Party",
        "default_likelihood": 3,
    },
]


DEFAULT_VULNERABILITIES = [
    {
        "vulnerability_code": "VUL-001",
        "name": "Unpatched Operating System",
        "category": "Patch Management",
        "description": (
            "The operating system is missing important security "
            "updates."
        ),
        "severity": "Critical",
        "remediation_guidance": (
            "Apply security patches through the approved patch "
            "management process."
        ),
    },
    {
        "vulnerability_code": "VUL-002",
        "name": "Multi-Factor Authentication Not Enabled",
        "category": "Identity and Access Management",
        "description": (
            "User authentication relies only on a password."
        ),
        "severity": "High",
        "remediation_guidance": (
            "Enable multi-factor authentication for privileged "
            "and remote accounts."
        ),
    },
    {
        "vulnerability_code": "VUL-003",
        "name": "Weak Password Policy",
        "category": "Identity and Access Management",
        "description": (
            "Password requirements do not adequately protect "
            "against guessing or credential attacks."
        ),
        "severity": "High",
        "remediation_guidance": (
            "Implement password length, complexity, lockout and "
            "compromised-password controls."
        ),
    },
    {
        "vulnerability_code": "VUL-004",
        "name": "Excessive Administrative Privileges",
        "category": "Access Control",
        "description": (
            "Users have more privileged access than required "
            "for their responsibilities."
        ),
        "severity": "Critical",
        "remediation_guidance": (
            "Apply least privilege and regularly review "
            "privileged access."
        ),
    },
    {
        "vulnerability_code": "VUL-005",
        "name": "Backup Restoration Not Tested",
        "category": "Business Continuity",
        "description": (
            "Backups exist, but restoration procedures have not "
            "been regularly tested."
        ),
        "severity": "High",
        "remediation_guidance": (
            "Schedule backup restoration tests and document "
            "the results."
        ),
    },
    {
        "vulnerability_code": "VUL-006",
        "name": "Insufficient Security Awareness",
        "category": "Human Resources Security",
        "description": (
            "Employees have not received regular cybersecurity "
            "awareness and phishing training."
        ),
        "severity": "High",
        "remediation_guidance": (
            "Conduct regular awareness training and phishing "
            "simulations."
        ),
    },
]


def seed_initial_data(db: Session) -> None:
    for role_data in DEFAULT_ROLES:
        existing_role = db.scalar(
            select(models.Role).where(
                models.Role.name == role_data["name"]
            )
        )

        if existing_role is None:
            db.add(models.Role(**role_data))

    for department_data in DEFAULT_DEPARTMENTS:
        existing_department = db.scalar(
            select(models.Department).where(
                models.Department.name
                == department_data["name"]
            )
        )

        if existing_department is None:
            db.add(
                models.Department(
                    **department_data,
                    description=(
                        f"{department_data['name']} department "
                        "of AutoSecure Manufacturing GmbH."
                    ),
                )
            )

    for threat_data in DEFAULT_THREATS:
        existing_threat = db.scalar(
            select(models.Threat).where(
                models.Threat.threat_code
                == threat_data["threat_code"]
            )
        )

        if existing_threat is None:
            db.add(models.Threat(**threat_data))

    for vulnerability_data in DEFAULT_VULNERABILITIES:
        existing_vulnerability = db.scalar(
            select(models.Vulnerability).where(
                models.Vulnerability.vulnerability_code
                == vulnerability_data["vulnerability_code"]
            )
        )

        if existing_vulnerability is None:
            db.add(
                models.Vulnerability(
                    **vulnerability_data
                )
            )

    db.commit()