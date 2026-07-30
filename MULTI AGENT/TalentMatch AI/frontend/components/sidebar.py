import streamlit as st
from models.schemas import JobRequisition

def render_sidebar() -> JobRequisition:
    """Render sidebar inputs and return structured JobRequisition."""
    st.sidebar.markdown("## 🧑‍💼 Requisition Parameters")

    job_title = st.sidebar.text_input(
        "Job Title / Role",
        value="",
        placeholder="e.g. Senior Backend Engineer"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💰 Salary Filter (EGP)")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        salary_min = st.number_input("Min Salary", min_value=0, value=0, step=500)
    with col2:
        salary_max = st.number_input("Max Salary", min_value=0, value=0, step=1000)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Priority Focus")
    priority_options = {
        "Balanced (Recommended)": "balanced",
        "Lowest Salary": "salary",
        "Experience & Interview Rating": "experience_rating",
        "Fast Hire Focus": "fast_hire"
    }
    selected_priority_label = st.sidebar.radio(
        "What matters most to you?",
        options=list(priority_options.keys())
    )
    priority = priority_options[selected_priority_label]

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Must-Have Skills")
    must_haves_raw = st.sidebar.text_area(
        "Comma separated skills",
        placeholder="e.g. Python, AWS, 5+ Years, Team Leadership"
    )
    must_have_skills = [s.strip() for s in must_haves_raw.split(",") if s.strip()]

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌐 Sourcing Channels")
    source_options = ["LinkedIn", "Indeed", "Wuzzuf", "Internal Referrals", "Company Careers"]
    selected_sources = []

    col_a, col_b = st.sidebar.columns(2)
    for idx, source in enumerate(source_options):
        # Default checked for LinkedIn, Indeed, Wuzzuf, Internal Referrals
        default_val = True if source != "Company Careers" else False
        with (col_a if idx % 2 == 0 else col_b):
            if st.checkbox(source, value=default_val, key=f"chk_{source}"):
                selected_sources.append(source)

    return JobRequisition(
        job_title=job_title,
        salary_min=float(salary_min) if salary_min > 0 else None,
        salary_max=float(salary_max) if salary_max > 0 else None,
        must_have_skills=must_have_skills,
        priority=priority,
        selected_sources=selected_sources if selected_sources else source_options[:4]
    )
