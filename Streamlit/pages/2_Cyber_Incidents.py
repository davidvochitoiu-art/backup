import streamlit as st
import pandas as pd
from app.services.database_manager import DatabaseManager
from app.models.security_incident import SecurityIncident

st.set_page_config(page_title="Cyber Incidents", layout="wide")

# Login check
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Please log in first.")
    st.switch_page("Home.py")

st.title("🛡️ Cybersecurity Incidents Analysis")

db = DatabaseManager("DATA/intelligence_platform.db")

# Load incidents (NO created_at column)
rows = db.fetch_all("""
    SELECT incident_id, category, severity, status, description
    FROM cyber_incidents
""")

incidents = [
    SecurityIncident(
        incident_id=row[0],
        incident_type=row[1],
        severity=row[2],
        status=row[3],
        description=row[4]
    )
    for row in rows
]

df = pd.DataFrame([{
    "ID": inc.get_id(),
    "Category": inc.get_incident_type(),
    "Severity": inc.get_severity(),
    "Status": inc.get_status(),
    "Description": inc.get_description(),
    "Severity Level (1–4)": inc.get_severity_level()
} for inc in incidents])


# ================= FILTER SECTION =================
st.subheader("Filters")

severity_filter = st.selectbox("Filter by Severity", ["All"] + sorted(df["Severity"].unique().tolist()))
status_filter = st.selectbox("Filter by Status", ["All"] + sorted(df["Status"].unique().tolist()))

filtered_df = df.copy()

if severity_filter != "All":
    filtered_df = filtered_df[filtered_df["Severity"].str.lower() == severity_filter.lower()]

if status_filter != "All":
    filtered_df = filtered_df[filtered_df["Status"].str.lower() == status_filter.lower()]

# ================= TABLE =================
st.subheader("Incident Table")
st.dataframe(filtered_df, use_container_width=True)


# ================= CHARTS =================
st.markdown("---")
st.header("📊 Cyber Incident Analytics Dashboard")

col1, col2 = st.columns(2)

# ----------------------------------------------------------
# Chart 1 — Severity Bar Chart
# ----------------------------------------------------------
with col1:
    st.subheader("Severity Distribution")
    st.bar_chart(filtered_df["Severity"].value_counts())

# ----------------------------------------------------------
# Chart 2 — Category Bar Chart
# ----------------------------------------------------------
with col2:
    st.subheader("Incident Categories")
    st.bar_chart(filtered_df["Category"].value_counts())

# ----------------------------------------------------------
# SECOND ROW — PIE CHARTS
# ----------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Severity Breakdown (Pie Chart)")
    pie1 = filtered_df["Severity"].value_counts().plot.pie(
        autopct="%1.1f%%", ylabel="", figsize=(5, 5)
    ).get_figure()
    st.pyplot(pie1)

with col4:
    st.subheader("Status Breakdown (Pie Chart)")
    pie2 = filtered_df["Status"].value_counts().plot.pie(
        autopct="%1.1f%%", ylabel="", figsize=(5, 5)
    ).get_figure()
    st.pyplot(pie2)
