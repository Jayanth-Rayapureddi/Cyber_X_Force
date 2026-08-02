import os
from datetime import date, datetime, time
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000").rstrip("/")
REQUEST_TIMEOUT = 12

st.set_page_config(
    page_title="Cyber_X_Force",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    .hero {
        padding: 1.2rem 1.35rem;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(35,92,171,0.28), rgba(20,25,38,0.45));
        margin-bottom: 1.2rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 2.1rem;
    }
    .hero p {
        margin: 0.35rem 0 0 0;
        opacity: 0.75;
    }
    .kpi-card {
        padding: 1rem 1.05rem;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        background: rgba(255,255,255,0.025);
        min-height: 112px;
    }
    .kpi-label {
        opacity: 0.72;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 750;
        margin-top: 0.25rem;
    }
    .kpi-note {
        opacity: 0.62;
        font-size: 0.78rem;
        margin-top: 0.2rem;
    }
    .section-card {
        padding: 1rem;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        background: rgba(255,255,255,0.018);
        margin-bottom: 0.75rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.22rem 0.55rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        background: rgba(70,130,220,0.18);
        border: 1px solid rgba(120,170,255,0.28);
    }
    .danger-badge {
        display: inline-block;
        padding: 0.22rem 0.55rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        background: rgba(225,70,70,0.16);
        border: 1px solid rgba(255,105,105,0.3);
    }
    .warn-badge {
        display: inline-block;
        padding: 0.22rem 0.55rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        background: rgba(230,170,50,0.16);
        border: 1px solid rgba(255,205,90,0.3);
    }
    .success-badge {
        display: inline-block;
        padding: 0.22rem 0.55rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        background: rgba(50,190,125,0.16);
        border: 1px solid rgba(90,230,160,0.3);
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def dt_value(day: date, clock: time = time(0, 0)) -> str:
    return datetime.combine(day, clock).isoformat()


def api_request(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    try:
        response = requests.request(
            method,
            f"{API_BASE_URL}{path}",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code >= 400:
            detail: Any = response.text
            try:
                detail = response.json().get("detail", detail)
            except ValueError:
                pass
            st.error(f"{method} {path} failed: {detail}")
            return None
        if response.status_code == 204:
            return True
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Backend request failed for {path}: {exc}")
        return None


def api_get(path: str) -> Any:
    return api_request("GET", path)


def api_post(path: str, payload: dict[str, Any]) -> Any:
    return api_request("POST", path, payload)


def api_put(path: str, payload: dict[str, Any]) -> Any:
    return api_request("PUT", path, payload)


def clean_frame(records: list[dict[str, Any]], preferred: list[str]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    frame = pd.DataFrame(records)
    visible = [column for column in preferred if column in frame.columns]
    remaining = [
        column
        for column in frame.columns
        if column not in visible
        and column not in {"created_at", "updated_at", "hashed_password"}
    ]
    return frame[visible + remaining]


def show_table(
    records: list[dict[str, Any]],
    preferred: list[str],
    empty_message: str,
) -> None:
    frame = clean_frame(records, preferred)
    if frame.empty:
        st.info(empty_message)
        return
    st.dataframe(frame, use_container_width=True, hide_index=True)


def kpi(label: str, value: Any, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge_class(value: str) -> str:
    lowered = value.lower()
    if any(word in lowered for word in ["critical", "non-compliant", "overdue", "major"]):
        return "danger-badge"
    if any(word in lowered for word in ["high", "planned", "open", "in progress", "partial"]):
        return "warn-badge"
    if any(word in lowered for word in ["implemented", "compliant", "completed", "closed", "verified"]):
        return "success-badge"
    return "status-badge"


def page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dashboard_page() -> None:
    page_header(
        "🛡️ Cyber_X_Force",
        "Executive view of the ISO/IEC 27001 risk, compliance, audit and incident posture.",
    )
    management = api_get("/management/dashboard")
    compliance = api_get("/compliance/dashboard")
    risks = api_get("/risks") or []
    incidents = api_get("/incidents") or []
    findings = api_get("/audit-findings") or []

    if not management:
        return

    row1 = st.columns(4)
    with row1[0]:
        kpi("Total Assets", management.get("total_assets", 0), "Registered information assets")
    with row1[1]:
        kpi("Total Risks", management.get("total_risks", 0), "Risks in the register")
    with row1[2]:
        kpi("Critical Risks", management.get("critical_risks", 0), "Immediate management attention")
    with row1[3]:
        kpi("Compliance", f"{management.get('compliance_percentage', 0):.2f}%", "Applicable controls implemented")

    row2 = st.columns(4)
    with row2[0]:
        kpi("Open Incidents", management.get("open_incidents", 0), "Not yet closed")
    with row2[1]:
        kpi("Open Findings", management.get("open_audit_findings", 0), "Audit findings requiring action")
    with row2[2]:
        kpi("Overdue Actions", management.get("overdue_corrective_actions", 0), "Corrective actions past due")
    with row2[3]:
        kpi("API Status", "Connected", API_BASE_URL)

    st.write("")
    left, right = st.columns(2)

    with left:
        st.subheader("Risk profile")
        if risks:
            risk_df = pd.DataFrame(risks)
            counts = (
                risk_df["inherent_level"]
                .value_counts()
                .rename_axis("level")
                .reset_index(name="count")
            )
            fig = px.bar(
                counts,
                x="level",
                y="count",
                text_auto=True,
                category_orders={"level": ["Low", "Medium", "High", "Critical"]},
            )
            fig.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No risk data is available.")

    with right:
        st.subheader("Compliance readiness")
        percentage = float(management.get("compliance_percentage", 0))
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=percentage,
                number={"suffix": "%"},
                gauge={"axis": {"range": [0, 100]}},
            )
        )
        gauge.update_layout(height=340, margin=dict(l=25, r=25, t=15, b=10))
        st.plotly_chart(gauge, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Control status")
        status_data = (compliance or {}).get("status_distribution", [])
        if status_data:
            fig = px.pie(
                pd.DataFrame(status_data),
                names="status",
                values="count",
                hole=0.52,
            )
            fig.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No control-status data is available.")

    with right:
        st.subheader("Current operational workload")
        workload = pd.DataFrame(
            [
                {"area": "Open incidents", "count": management.get("open_incidents", 0)},
                {"area": "Open findings", "count": management.get("open_audit_findings", 0)},
                {"area": "Overdue actions", "count": management.get("overdue_corrective_actions", 0)},
            ]
        )
        fig = px.bar(workload, x="area", y="count", text_auto=True)
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top overdue controls")
    overdue = (compliance or {}).get("top_overdue_controls", [])
    if not overdue:
        st.success("No overdue controls.")
    else:
        columns = st.columns(min(3, len(overdue)))
        for index, control in enumerate(overdue[:3]):
            with columns[index]:
                st.markdown(
                    f"""
                    <div class="section-card">
                        <span class="danger-badge">{control.get('days_overdue', 0)} days overdue</span>
                        <h3>{control.get('control_code', '')}</h3>
                        <b>{control.get('title', '')}</b><br><br>
                        Owner: {control.get('owner') or 'Unassigned'}<br>
                        Progress: {control.get('implementation_percentage', 0)}%
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if incidents or findings:
        st.subheader("Recent governance activity")
        activity_left, activity_right = st.columns(2)
        with activity_left:
            show_table(
                incidents[:5],
                ["incident_code", "title", "severity", "status", "assigned_to", "detected_at"],
                "No incidents.",
            )
        with activity_right:
            show_table(
                findings[:5],
                ["finding_code", "title", "finding_type", "severity", "status", "owner", "due_date"],
                "No findings.",
            )


def assets_page() -> None:
    page_header("Assets", "Register, classify and review organizational information assets.")
    assets = api_get("/assets") or []
    departments = api_get("/departments") or []

    search_col, type_col, criticality_col = st.columns([2, 1, 1])
    search = search_col.text_input("Search assets", placeholder="Code, name, type or location")
    asset_types = sorted({item.get("asset_type", "") for item in assets if item.get("asset_type")})
    selected_type = type_col.selectbox("Asset type", ["All"] + asset_types)
    criticalities = ["All", "Critical", "High", "Medium", "Low"]
    selected_criticality = criticality_col.selectbox("Criticality", criticalities)

    filtered = assets
    if search:
        token = search.lower()
        filtered = [
            item for item in filtered
            if token in " ".join(
                str(item.get(key, "")).lower()
                for key in ["asset_code", "name", "asset_type", "location"]
            )
        ]
    if selected_type != "All":
        filtered = [item for item in filtered if item.get("asset_type") == selected_type]
    if selected_criticality != "All":
        filtered = [item for item in filtered if item.get("criticality") == selected_criticality]

    show_table(
        filtered,
        ["asset_code", "name", "asset_type", "criticality", "location", "confidentiality", "integrity", "availability", "is_active"],
        "No matching assets.",
    )

    with st.expander("➕ Register a new asset"):
        department_options = {
            f"{item['name']} (ID {item['id']})": item["id"]
            for item in departments
        }
        with st.form("asset_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            asset_code = c1.text_input("Asset code", value="AST-")
            name = c2.text_input("Asset name")
            asset_type = c1.selectbox(
                "Asset type",
                ["Server", "Database", "Application", "Workstation", "Network", "Cloud Service", "Information", "Other"],
            )
            location = c2.text_input("Location")
            description = st.text_area("Description")
            c1, c2, c3 = st.columns(3)
            confidentiality = c1.slider("Confidentiality", 1, 5, 3)
            integrity = c2.slider("Integrity", 1, 5, 3)
            availability = c3.slider("Availability", 1, 5, 3)
            department_label = st.selectbox(
                "Department",
                list(department_options) if department_options else ["No department available"],
            )
            submitted = st.form_submit_button("Create asset", use_container_width=True)

        if submitted:
            if not department_options:
                st.error("Create a department before registering an asset.")
            else:
                created = api_post(
                    "/assets",
                    {
                        "asset_code": asset_code,
                        "name": name,
                        "asset_type": asset_type,
                        "description": description or None,
                        "location": location or None,
                        "confidentiality": confidentiality,
                        "integrity": integrity,
                        "availability": availability,
                        "department_id": department_options[department_label],
                        "owner_id": None,
                    },
                )
                if created:
                    st.success("Asset created.")
                    st.rerun()


def risk_heatmap(risks: list[dict[str, Any]]) -> None:
    matrix = [[0 for _ in range(5)] for _ in range(5)]
    for risk in risks:
        likelihood = int(risk.get("likelihood", 0))
        impact = int(risk.get("impact", 0))
        if 1 <= likelihood <= 5 and 1 <= impact <= 5:
            matrix[5 - likelihood][impact - 1] += 1
    fig = px.imshow(
        matrix,
        labels={"x": "Impact", "y": "Likelihood", "color": "Risk count"},
        x=[1, 2, 3, 4, 5],
        y=[5, 4, 3, 2, 1],
        text_auto=True,
        aspect="auto",
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)


def risks_page() -> None:
    page_header("Risk Register", "Prioritize inherent and residual cybersecurity risks.")
    risks = api_get("/risks") or []

    search_col, level_col, status_col = st.columns([2, 1, 1])
    search = search_col.text_input("Search risks", placeholder="Risk code, title, owner or treatment")
    level = level_col.selectbox("Risk level", ["All", "Critical", "High", "Medium", "Low"])
    status_value = status_col.selectbox("Status", ["All", "Open", "Under Treatment", "Accepted", "Closed"])

    filtered = risks
    if search:
        token = search.lower()
        filtered = [
            item for item in filtered
            if token in " ".join(
                str(item.get(key, "")).lower()
                for key in ["risk_code", "title", "risk_owner", "treatment_option"]
            )
        ]
    if level != "All":
        filtered = [item for item in filtered if item.get("inherent_level") == level]
    if status_value != "All":
        filtered = [item for item in filtered if item.get("status") == status_value]

    if not filtered:
        st.info("No matching risks.")
    else:
        for risk in filtered:
            badge = badge_class(str(risk.get("inherent_level", "")))
            with st.container():
                st.markdown(
                    f"""
                    <div class="section-card">
                        <span class="{badge}">{risk.get('inherent_level', '')}</span>
                        <span class="status-badge">{risk.get('status', '')}</span>
                        <h3>{risk.get('risk_code', '')} — {risk.get('title', '')}</h3>
                        <b>Score:</b> {risk.get('inherent_score', '')}
                        &nbsp;&nbsp; <b>Likelihood:</b> {risk.get('likelihood', '')}/5
                        &nbsp;&nbsp; <b>Impact:</b> {risk.get('impact', '')}/5
                        &nbsp;&nbsp; <b>Treatment:</b> {risk.get('treatment_option', '')}<br>
                        <span style="opacity:.72">{risk.get('description') or 'No description'}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.subheader("5 × 5 risk heat map")
    risk_heatmap(risks)

    show_table(
        risks,
        ["risk_code", "title", "inherent_level", "inherent_score", "likelihood", "impact", "status", "treatment_option", "risk_owner", "residual_level"],
        "No risks have been recorded.",
    )


def controls_page() -> None:
    page_header("ISO Controls", "Monitor control ownership, status and implementation progress.")
    controls = api_get("/controls") or []

    c1, c2, c3 = st.columns([2, 1, 1])
    search = c1.text_input("Search controls", placeholder="Control code, title or owner")
    categories = sorted({item.get("category") for item in controls if item.get("category")})
    selected_category = c2.selectbox("Category", ["All"] + categories)
    selected_status = c3.selectbox(
        "Status",
        ["All", "Implemented", "In Progress", "Planned", "Not Started", "Not Applicable"],
    )

    filtered = controls
    if search:
        token = search.lower()
        filtered = [
            item for item in filtered
            if token in " ".join(
                str(item.get(key, "")).lower()
                for key in ["control_code", "title", "owner"]
            )
        ]
    if selected_category != "All":
        filtered = [item for item in filtered if item.get("category") == selected_category]
    if selected_status != "All":
        filtered = [item for item in filtered if item.get("implementation_status") == selected_status]

    if not filtered:
        st.info("No matching controls.")
    else:
        for control in filtered:
            status = str(control.get("implementation_status", ""))
            st.markdown(
                f"""
                <div class="section-card">
                    <span class="{badge_class(status)}">{status}</span>
                    <h3>{control.get('control_code', '')} — {control.get('title', '')}</h3>
                    <b>Owner:</b> {control.get('owner') or 'Unassigned'}
                    &nbsp;&nbsp; <b>Category:</b> {control.get('category', '')}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(int(control.get("implementation_percentage", 0)) / 100)
            st.caption(f"{control.get('implementation_percentage', 0)}% implemented")

    show_table(
        filtered,
        ["control_code", "title", "category", "implementation_status", "implementation_percentage", "owner", "target_date", "last_reviewed_at"],
        "No controls available.",
    )


def compliance_page() -> None:
    page_header("Compliance", "Assess control conformance and monitor ISO/IEC 27001 readiness.")
    summary = api_get("/compliance/summary") or {}
    overdue = api_get("/compliance/overdue-controls") or []
    assessments = api_get("/compliance-assessments") or []
    controls = api_get("/controls") or []

    cols = st.columns(4)
    with cols[0]:
        kpi("Total Controls", summary.get("total_controls", 0), "In the control library")
    with cols[1]:
        kpi("Implemented", summary.get("implemented", 0), "Fully implemented controls")
    with cols[2]:
        kpi("Compliance", f"{summary.get('overall_compliance_percentage', 0):.2f}%", "Excludes not-applicable controls")
    with cols[3]:
        kpi("Average Progress", f"{summary.get('average_implementation_percentage', 0):.2f}%", "Average implementation percentage")

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Compliance gauge")
        value = float(summary.get("overall_compliance_percentage", 0))
        fig = go.Figure(go.Indicator(mode="gauge+number", value=value, number={"suffix": "%"}, gauge={"axis": {"range": [0, 100]}}))
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Assessment status")
        if assessments:
            frame = pd.DataFrame(assessments)
            distribution = frame["compliance_status"].value_counts().rename_axis("status").reset_index(name="count")
            fig = px.pie(distribution, names="status", values="count", hole=0.5)
            fig.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No assessments have been recorded.")

    st.subheader("Overdue controls")
    show_table(
        overdue,
        ["control_code", "title", "owner", "implementation_status", "implementation_percentage", "target_date", "days_overdue"],
        "No overdue controls.",
    )

    with st.expander("➕ Record a compliance assessment"):
        control_options = {
            f"{item['control_code']} — {item['title']}": item["id"]
            for item in controls
        }
        with st.form("assessment_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            assessment_code = c1.text_input("Assessment code", value="ASM-")
            control_label = c2.selectbox("ISO control", list(control_options) if control_options else ["No controls"])
            compliance_status = c1.selectbox(
                "Compliance status",
                ["Not Assessed", "Compliant", "Partially Compliant", "Non-Compliant", "Not Applicable"],
            )
            compliance_score = c2.slider("Compliance score", 0, 100, 50)
            assessor = c1.text_input("Assessor")
            assessment_date = c2.date_input("Assessment date", value=date.today())
            findings = st.text_area("Findings")
            recommendations = st.text_area("Recommendations")
            evidence_reference = st.text_input("Evidence reference")
            next_review = st.date_input("Next review date", value=date.today())
            submitted = st.form_submit_button("Create assessment", use_container_width=True)
        if submitted and control_options:
            created = api_post(
                "/compliance-assessments",
                {
                    "assessment_code": assessment_code,
                    "control_id": control_options[control_label],
                    "compliance_status": compliance_status,
                    "compliance_score": compliance_score,
                    "assessor": assessor,
                    "assessment_date": dt_value(assessment_date),
                    "findings": findings or None,
                    "recommendations": recommendations or None,
                    "evidence_reference": evidence_reference or None,
                    "next_review_date": dt_value(next_review),
                },
            )
            if created:
                st.success("Compliance assessment created.")
                st.rerun()

    st.subheader("Assessment history")
    show_table(
        assessments,
        ["assessment_code", "control_id", "compliance_status", "compliance_score", "assessor", "assessment_date", "next_review_date"],
        "No compliance assessments.",
    )


def evidence_page() -> None:
    page_header("Evidence Repository", "Register policies, reports, screenshots and other audit evidence.")
    evidence = api_get("/evidence") or []
    controls = api_get("/controls") or []
    assessments = api_get("/compliance-assessments") or []

    verified = sum(bool(item.get("is_verified")) for item in evidence)
    cols = st.columns(3)
    with cols[0]:
        kpi("Evidence Records", len(evidence), "Registered evidence items")
    with cols[1]:
        kpi("Verified", verified, "Evidence reviewed by an auditor")
    with cols[2]:
        kpi("Pending Verification", len(evidence) - verified, "Still awaiting review")

    with st.expander("➕ Add evidence metadata"):
        control_options = {"None": None} | {
            f"{item['control_code']} — {item['title']}": item["id"]
            for item in controls
        }
        assessment_options = {"None": None} | {
            item["assessment_code"]: item["id"]
            for item in assessments
        }
        with st.form("evidence_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            evidence_code = c1.text_input("Evidence code", value="EVD-")
            title = c2.text_input("Title")
            evidence_type = c1.selectbox(
                "Evidence type",
                ["Policy", "Procedure", "Report", "Screenshot", "Log", "Certificate", "Spreadsheet", "Other"],
            )
            owner = c2.text_input("Owner")
            description = st.text_area("Description")
            reference_location = st.text_input(
                "Reference location",
                placeholder="Local path, SharePoint link, document reference or repository URL",
            )
            c1, c2 = st.columns(2)
            control_label = c1.selectbox("Related control", list(control_options))
            assessment_label = c2.selectbox("Related assessment", list(assessment_options))
            collected_at = c1.date_input("Collected date", value=date.today())
            valid_until = c2.date_input("Valid until", value=date.today())
            is_verified = st.checkbox("Verified")
            verification_notes = st.text_area("Verification notes")
            submitted = st.form_submit_button("Create evidence record", use_container_width=True)
        if submitted:
            created = api_post(
                "/evidence",
                {
                    "evidence_code": evidence_code,
                    "title": title,
                    "evidence_type": evidence_type,
                    "description": description or None,
                    "reference_location": reference_location,
                    "control_id": control_options[control_label],
                    "assessment_id": assessment_options[assessment_label],
                    "owner": owner or None,
                    "collected_at": dt_value(collected_at),
                    "valid_until": dt_value(valid_until),
                    "is_verified": is_verified,
                    "verification_notes": verification_notes or None,
                },
            )
            if created:
                st.success("Evidence record created.")
                st.rerun()

    show_table(
        evidence,
        ["evidence_code", "title", "evidence_type", "owner", "control_id", "assessment_id", "collected_at", "valid_until", "is_verified", "reference_location"],
        "No evidence records have been added.",
    )


def audits_page() -> None:
    page_header("Audits and Findings", "Plan internal audits and track non-conformities.")
    audits = api_get("/audits") or []
    findings = api_get("/audit-findings") or []
    controls = api_get("/controls") or []

    tab1, tab2 = st.tabs(["Audits", "Audit Findings"])

    with tab1:
        with st.expander("➕ Create an audit"):
            with st.form("audit_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                audit_code = c1.text_input("Audit code", value="AUD-")
                title = c2.text_input("Audit title")
                audit_type = c1.selectbox("Audit type", ["Internal", "Supplier", "Certification", "Follow-up"])
                lead_auditor = c2.text_input("Lead auditor")
                scope = st.text_area("Scope")
                c1, c2 = st.columns(2)
                start_date = c1.date_input("Planned start", value=date.today())
                end_date = c2.date_input("Planned end", value=date.today())
                status_value = st.selectbox("Status", ["Planned", "In Progress", "Completed", "Cancelled"])
                summary = st.text_area("Summary")
                submitted = st.form_submit_button("Create audit", use_container_width=True)
            if submitted:
                created = api_post(
                    "/audits",
                    {
                        "audit_code": audit_code,
                        "title": title,
                        "audit_type": audit_type,
                        "scope": scope,
                        "lead_auditor": lead_auditor,
                        "planned_start_date": dt_value(start_date),
                        "planned_end_date": dt_value(end_date),
                        "status": status_value,
                        "summary": summary or None,
                    },
                )
                if created:
                    st.success("Audit created.")
                    st.rerun()

        show_table(
            audits,
            ["audit_code", "title", "audit_type", "lead_auditor", "planned_start_date", "planned_end_date", "status"],
            "No audits have been created.",
        )

    with tab2:
        audit_options = {f"{item['audit_code']} — {item['title']}": item["id"] for item in audits}
        control_options = {"None": None} | {
            f"{item['control_code']} — {item['title']}": item["id"]
            for item in controls
        }
        with st.expander("➕ Record an audit finding"):
            with st.form("finding_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                finding_code = c1.text_input("Finding code", value="FND-")
                audit_label = c2.selectbox("Audit", list(audit_options) if audit_options else ["No audits"])
                title = c1.text_input("Finding title")
                control_label = c2.selectbox("Related control", list(control_options))
                finding_type = c1.selectbox(
                    "Finding type",
                    ["Observation", "Opportunity for Improvement", "Minor Non-Conformity", "Major Non-Conformity"],
                )
                severity = c2.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
                description = st.text_area("Description")
                root_cause = st.text_area("Root cause")
                owner = c1.text_input("Owner")
                due_date = c2.date_input("Due date", value=date.today())
                status_value = st.selectbox("Status", ["Open", "Under Review", "Remediation", "Verified", "Closed"])
                submitted = st.form_submit_button("Create finding", use_container_width=True)
            if submitted and audit_options:
                created = api_post(
                    "/audit-findings",
                    {
                        "finding_code": finding_code,
                        "audit_id": audit_options[audit_label],
                        "control_id": control_options[control_label],
                        "title": title,
                        "finding_type": finding_type,
                        "severity": severity,
                        "description": description,
                        "root_cause": root_cause or None,
                        "owner": owner or None,
                        "due_date": dt_value(due_date),
                        "status": status_value,
                    },
                )
                if created:
                    st.success("Audit finding created.")
                    st.rerun()

        show_table(
            findings,
            ["finding_code", "title", "finding_type", "severity", "status", "owner", "due_date", "audit_id", "control_id"],
            "No audit findings.",
        )


def actions_page() -> None:
    page_header("Corrective Actions", "Track remediation from open action through verification.")
    actions = api_get("/corrective-actions") or []
    findings = api_get("/audit-findings") or []

    finding_options = {
        f"{item['finding_code']} — {item['title']}": item["id"]
        for item in findings
    }
    with st.expander("➕ Create a corrective action"):
        with st.form("corrective_action_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            action_code = c1.text_input("Action code", value="CAP-")
            finding_label = c2.selectbox("Audit finding", list(finding_options) if finding_options else ["No findings"])
            owner = c1.text_input("Action owner")
            target_date = c2.date_input("Target date", value=date.today())
            description = st.text_area("Action description")
            status_value = c1.selectbox("Status", ["Open", "In Progress", "Completed", "Verified", "Cancelled"])
            completion = c2.slider("Completion percentage", 0, 100, 0)
            verification = st.text_area("Verification result")
            submitted = st.form_submit_button("Create corrective action", use_container_width=True)
        if submitted and finding_options:
            created = api_post(
                "/corrective-actions",
                {
                    "action_code": action_code,
                    "finding_id": finding_options[finding_label],
                    "action_description": description,
                    "action_owner": owner,
                    "target_date": dt_value(target_date),
                    "status": status_value,
                    "completion_percentage": completion,
                    "completion_date": dt_value(date.today()) if completion == 100 else None,
                    "verification_result": verification or None,
                },
            )
            if created:
                st.success("Corrective action created.")
                st.rerun()

    statuses = ["Open", "In Progress", "Completed", "Verified"]
    columns = st.columns(4)
    for index, status_value in enumerate(statuses):
        with columns[index]:
            st.subheader(status_value)
            matching = [item for item in actions if item.get("status") == status_value]
            if not matching:
                st.caption("No actions")
            for item in matching:
                st.markdown(
                    f"""
                    <div class="section-card">
                        <b>{item.get('action_code', '')}</b><br>
                        {item.get('action_description', '')}<br><br>
                        Owner: {item.get('action_owner', '')}<br>
                        Due: {str(item.get('target_date', ''))[:10]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(int(item.get("completion_percentage", 0)) / 100)

    show_table(
        actions,
        ["action_code", "action_description", "action_owner", "status", "completion_percentage", "target_date", "completion_date", "finding_id"],
        "No corrective actions.",
    )


def incidents_page() -> None:
    page_header("Incidents", "Record, triage, contain and close cybersecurity incidents.")
    incidents = api_get("/incidents") or []
    assets = api_get("/assets") or []

    asset_options = {"None": None} | {
        f"{item['asset_code']} — {item['name']}": item["id"]
        for item in assets
    }

    with st.expander("➕ Report an incident"):
        with st.form("incident_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            incident_code = c1.text_input("Incident code", value="INC-")
            title = c2.text_input("Title")
            category = c1.selectbox(
                "Category",
                ["Malware", "Phishing", "Unauthorized Access", "Data Breach", "Service Disruption", "Insider Threat", "Other"],
            )
            severity = c2.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            description = st.text_area("Description")
            asset_label = c1.selectbox("Affected asset", list(asset_options))
            reported_by = c2.text_input("Reported by")
            assigned_to = c1.text_input("Assigned to")
            detected_date = c2.date_input("Detected date", value=date.today())
            status_value = st.selectbox(
                "Status",
                ["Reported", "Triaged", "Investigating", "Contained", "Recovered", "Closed"],
            )
            submitted = st.form_submit_button("Create incident", use_container_width=True)
        if submitted:
            created = api_post(
                "/incidents",
                {
                    "incident_code": incident_code,
                    "title": title,
                    "category": category,
                    "severity": severity,
                    "description": description,
                    "asset_id": asset_options[asset_label],
                    "reported_by": reported_by,
                    "assigned_to": assigned_to or None,
                    "detected_at": dt_value(detected_date),
                    "status": status_value,
                    "containment_summary": None,
                    "root_cause": None,
                    "lessons_learned": None,
                    "closed_at": dt_value(date.today()) if status_value == "Closed" else None,
                },
            )
            if created:
                st.success("Incident created.")
                st.rerun()

    severity_filter = st.multiselect(
        "Severity filter",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"],
    )
    filtered = [item for item in incidents if item.get("severity") in severity_filter]

    if filtered:
        cols = st.columns(3)
        for index, item in enumerate(filtered):
            with cols[index % 3]:
                severity = str(item.get("severity", ""))
                st.markdown(
                    f"""
                    <div class="section-card">
                        <span class="{badge_class(severity)}">{severity}</span>
                        <span class="status-badge">{item.get('status', '')}</span>
                        <h3>{item.get('incident_code', '')}</h3>
                        <b>{item.get('title', '')}</b><br><br>
                        Category: {item.get('category', '')}<br>
                        Assigned: {item.get('assigned_to') or 'Unassigned'}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No matching incidents.")

    show_table(
        filtered,
        ["incident_code", "title", "category", "severity", "status", "assigned_to", "reported_by", "detected_at", "asset_id"],
        "No incidents.",
    )


def system_status_page() -> None:
    page_header("System Status", "Verify application and database connectivity.")
    health = api_get("/health")
    root = api_get("/")

    cols = st.columns(3)
    with cols[0]:
        kpi("Application", (root or {}).get("application", "Unavailable"), (root or {}).get("status", "unknown"))
    with cols[1]:
        kpi("Database", (health or {}).get("database", "Unavailable"), (health or {}).get("status", "unknown"))
    with cols[2]:
        kpi("Version", (root or {}).get("version", "Unknown"), API_BASE_URL)

    with st.expander("Technical response"):
        st.json({"api_base_url": API_BASE_URL, "application": root, "health": health})


PAGES = {
    "🏠 Dashboard": dashboard_page,
    "🗂️ Assets": assets_page,
    "⚠️ Risk Register": risks_page,
    "🛡️ ISO Controls": controls_page,
    "✅ Compliance": compliance_page,
    "📁 Evidence": evidence_page,
    "🔎 Audits and Findings": audits_page,
    "🧰 Corrective Actions": actions_page,
    "🚨 Incidents": incidents_page,
    "⚙️ System Status": system_status_page,
}

with st.sidebar:
    st.markdown("## 🛡️ Cyber_X_Force")
    st.caption("ISO/IEC 27001 GRC Platform")
    selected_page = st.radio(
        "Navigation",
        list(PAGES),
        label_visibility="collapsed",
    )
    st.divider()
    health = api_get("/health")
    if health and health.get("status") == "healthy":
        st.success("Backend connected")
    else:
        st.error("Backend unavailable")
    st.caption(API_BASE_URL)

PAGES[selected_page]()
