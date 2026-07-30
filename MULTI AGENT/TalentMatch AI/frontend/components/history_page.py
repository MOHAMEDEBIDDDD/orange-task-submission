import streamlit as st
import pandas as pd
import plotly.express as px
from tools.cache_tool import get_all_search_history, get_salary_history_records

def render_history_tab():
    """Render Search History tab content."""
    st.markdown("## 🕐 Search History Log")
    records = get_all_search_history()

    if not records:
        st.info("No past searches recorded yet. Try running a search on the Search tab!")
        return

    df = pd.DataFrame(records)
    st.dataframe(
        df[["searched_at", "job_title", "top_candidate_name", "top_candidate_salary"]],
        column_config={
            "searched_at": "Search Date",
            "job_title": "Job Title",
            "top_candidate_name": "Top Candidate Found",
            "top_candidate_salary": st.column_config.NumberColumn("Top Candidate Salary (EGP)", format="%.2f EGP")
        },
        use_container_width=True,
        hide_index=True
    )

def render_salary_tracker_tab():
    """Render Salary Tracker tab content."""
    st.markdown("## 📈 Salary Tracker & Historical Trends")
    records = get_salary_history_records()

    if not records:
        st.info("No historical salary records collected yet. Run a search to populate salary tracker data!")
        return

    df = pd.DataFrame(records)
    st.markdown("##### 💵 Recorded Candidate Salary Expectation Variations Over Time")

    fig = px.line(
        df,
        x="recorded_at",
        y="expected_salary",
        color="candidate_name",
        line_dash="source",
        markers=True,
        labels={"recorded_at": "Date Recorded", "expected_salary": "Expected Salary (EGP)", "candidate_name": "Candidate"}
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
