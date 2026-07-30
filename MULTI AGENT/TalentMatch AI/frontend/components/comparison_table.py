import streamlit as st
import pandas as pd
from typing import List
from models.schemas import ScoredCandidate

def render_comparison_table(scored_candidates: List[ScoredCandidate]):
    """Render sortable, filterable interactive candidate comparison table."""
    st.markdown("### 📊 Comprehensive Candidate Comparison")

    data = []
    for sc in scored_candidates:
        c = sc.candidate
        ri = sc.reference_insight
        data.append({
            "Rank": f"#{scored_candidates.index(sc) + 1}",
            "Candidate Name": c.name,
            "Source Channel": c.source,
            "Expected Salary (EGP)": c.expected_salary,
            "Interview Score": f"⭐ {c.interview_score}" if c.interview_score else "N/A",
            "Fit Score": f"{sc.fit_score}/100",
            "Skills Match": f"{sc.skills_match_pct}%",
            "Within Salary Range": "✅ Yes" if sc.within_salary_range else "❌ Exceeded",
            "Verification Status": ri.verification_status.upper() if ri else "N/A",
            "Profile Link": c.profile_url
        })

    df = pd.DataFrame(data)

    # Render table using Streamlit column configuration
    st.dataframe(
        df,
        column_config={
            "Profile Link": st.column_config.LinkColumn("Profile Link", display_text="View Profile ↗"),
            "Expected Salary (EGP)": st.column_config.NumberColumn("Expected Salary (EGP)", format="%.2f EGP"),
            "Fit Score": st.column_config.TextColumn("Fit Score", help="0-100 score based on skills, salary & interview rating"),
        },
        use_container_width=True,
        hide_index=True
    )
