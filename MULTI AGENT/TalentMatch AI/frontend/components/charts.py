import streamlit as st
import plotly.express as px
import pandas as pd
from typing import List
from models.schemas import ScoredCandidate

def render_charts(scored_candidates: List[ScoredCandidate]):
    """Render interactive Plotly visual charts formatted for dark theme."""
    st.markdown("### 📈 Visual Analytics & Score Breakdown")

    col1, col2 = st.columns(2)

    df_data = []
    for sc in scored_candidates:
        c = sc.candidate
        df_data.append({
            "Short Name": c.name[:25] + ("..." if len(c.name) > 25 else ""),
            "Expected Salary": c.expected_salary or 0,
            "Source": c.source,
            "Fit Score": sc.fit_score,
            "Interview Score": c.interview_score or 0.0
        })

    df = pd.DataFrame(df_data)

    with col1:
        st.markdown("##### 💵 Expected Salary by Source")
        fig_salary = px.bar(
            df,
            x="Short Name",
            y="Expected Salary",
            color="Source",
            text="Expected Salary",
            labels={"Expected Salary": "Expected Salary (EGP)", "Short Name": "Candidate"},
            color_discrete_map={
                "LinkedIn": "#0A66C2",
                "Indeed": "#2557A7",
                "Wuzzuf": "#017AA1",
                "Internal Referrals": "#10B981",
                "Company Careers": "#F59E0B"
            }
        )
        fig_salary.update_traces(texttemplate='%{text:,.0f} EGP', textposition='outside', textfont=dict(color='#F8FAFC'))
        fig_salary.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC"),
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=True,
            xaxis=dict(gridcolor="#334155"),
            yaxis=dict(gridcolor="#334155")
        )
        st.plotly_chart(fig_salary, use_container_width=True)

    with col2:
        st.markdown("##### 🏆 Fit-for-Role Score Ranking")
        fig_score = px.bar(
            df,
            y="Short Name",
            x="Fit Score",
            color="Fit Score",
            orientation="h",
            text="Fit Score",
            color_continuous_scale="Viridis",
            labels={"Fit Score": "Fit Score (0-100)"}
        )
        fig_score.update_traces(textposition='inside', textfont=dict(color='#FFFFFF'))
        fig_score.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC"),
            margin=dict(l=20, r=20, t=30, b=20),
            yaxis=dict(autorange="reversed", gridcolor="#334155"),
            xaxis=dict(gridcolor="#334155")
        )
        st.plotly_chart(fig_score, use_container_width=True)
