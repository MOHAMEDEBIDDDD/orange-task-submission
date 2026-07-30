import streamlit as st
import sys
import asyncio
import os
from pathlib import Path

# Add project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Streamlit Page Configuration
st.set_page_config(
    page_title="TalentMatch AI — Multi-Agent Recruiting Intelligence",
    page_icon="🧑‍💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
CSS_PATH = Path(__file__).resolve().parent / "style.css"
if CSS_PATH.exists():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from models.schemas import JobRequisition, HiringReport
from frontend.components.sidebar import render_sidebar
from frontend.components.progress_tracker import render_progress
from frontend.components.top_candidate_card import render_top_candidate
from frontend.components.comparison_table import render_comparison_table
from frontend.components.charts import render_charts
from frontend.components.reference_summary import render_reference_insights
from frontend.components.history_page import render_history_tab, render_salary_tracker_tab
from crew.hiring_crew import run_talent_search
from utils.export_utils import export_to_pdf, export_to_excel

# Render Sidebar inputs
requisition: JobRequisition = render_sidebar()

# Application Hero Header
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🧑‍💼 TalentMatch AI</div>
    <div class="hero-subtitle">
        An autonomous multi-agent recruiting system that scans LinkedIn, Indeed, Wuzzuf, Internal Referrals & Company Careers simultaneously,
        evaluates candidate reference trust signals, and computes fit-for-role hiring recommendations.
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab_search, tab_history, tab_tracker, tab_about = st.tabs([
    "🔍 Live Candidate Search",
    "🕐 Search History",
    "📈 Salary Tracker",
    "ℹ️ Architecture & About"
])

with tab_search:
    st.markdown("### 🔎 Search & Compare Candidates")

    col_input, col_action = st.columns([3, 1])
    with col_input:
        st.info("Enter the job title and salary preferences in the sidebar, then click **Start Search**.")
    with col_action:
        search_clicked = st.button("🚀 Start Multi-Agent Search", type="primary")

    # State containers
    if 'current_report' not in st.session_state:
        st.session_state.current_report = None

    if search_clicked:
        if not requisition.job_title.strip():
            st.warning("⚠️ Please enter a job title in the sidebar before searching.")
        else:
            progress_container = st.empty()

            def progress_callback(stage: str, progress: float):
                with progress_container.container():
                    render_progress(stage, progress)

            try:
                report = asyncio.run(run_talent_search(requisition, progress_callback))
                st.session_state.current_report = report
                progress_container.empty()
                st.toast("✅ Search completed successfully!", icon="🎉")
            except Exception as e:
                progress_container.empty()
                st.error(f"❌ Search operation encountered an issue: {str(e)}")

    # Display Search Results
    if st.session_state.current_report:
        report: HiringReport = st.session_state.current_report

        # 1. Top Candidate & Runner Up
        render_top_candidate(report)

        st.markdown("---")

        # 2. Interactive Comparison Table
        render_comparison_table(report.all_scored_candidates)

        st.markdown("---")

        # 3. Visual Charts
        render_charts(report.all_scored_candidates)

        st.markdown("---")

        # 4. Reference Intelligence
        render_reference_insights(report.all_scored_candidates)

        st.markdown("---")

        # 5. Export Actions
        st.markdown("### 📥 Export Hiring Intelligence Report")
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            try:
                pdf_bytes = export_to_pdf(report)
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"TalentMatch_Report_{requisition.job_title.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as ex:
                st.error("PDF export setup ready.")

        with c2:
            try:
                excel_bytes = export_to_excel(report)
                st.download_button(
                    label="📊 Download Excel Data",
                    data=excel_bytes,
                    file_name=f"TalentMatch_Data_{requisition.job_title.replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as ex:
                st.error("Excel export setup ready.")

with tab_history:
    render_history_tab()

with tab_tracker:
    render_salary_tracker_tab()

with tab_about:
    st.markdown("""
    ## 🤖 TalentMatch AI Multi-Agent Architecture

    TalentMatch AI orchestrates **6 specialized CrewAI AI Agents** working in harmony:

    1. **Job Requisition Analyst Agent**: Transforms raw hiring requests into precise role specs.
    2. **Sourcing Agents**: Asynchronously sources candidate profiles across LinkedIn, Indeed, Wuzzuf, Internal Referrals, and Company Careers.
    3. **Aggregator / Deduplication Agent**: Deduplicates candidate profile variations using fuzzy token matching (`rapidfuzz`).
    4. **Reference Check Agent**: Analyzes candidate interview signals and endorsements, assigning verification flags.
    5. **Fit Scoring Agent**: Computes dynamic 0-100 **Fit-for-Role** scores based on salary, interview score, skills match, and priority weights.
    6. **Report Agent**: Synthesizes transparent hiring recommendations, top-candidate reasoning, and rejected summaries.
    """)
