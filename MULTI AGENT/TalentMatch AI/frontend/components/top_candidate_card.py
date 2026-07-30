import streamlit as st
from models.schemas import HiringReport

def render_top_candidate(report: HiringReport):
    """Render Top Candidate recommendation card and Runner-Up card with high-contrast dark design."""
    tc = report.top_candidate.candidate
    tc_score = report.top_candidate.fit_score

    st.markdown(f"""
    <div class="best-pick-card">
        <div class="best-pick-header">
            <span class="badge-best-pick">🏆 Top Recommendation (Best Fit)</span>
            <span class="store-tag">Sourced via {tc.source}</span>
        </div>
        <div style="display: flex; gap: 1.5rem; flex-wrap: wrap; align-items: center;">
            <img src="{tc.avatar_url}" style="width: 140px; height: 140px; object-fit: cover; border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.2);" />
            <div style="flex: 1; min-width: 250px;">
                <h2 style="margin: 0 0 0.5rem 0; color: #FFFFFF !important; font-size: 1.4rem; font-weight: 700;">{tc.name}</h2>
                <div style="font-size: 1.75rem; font-weight: 800; color: #34D399 !important; margin-bottom: 0.5rem;">
                    {tc.expected_salary:,.2f} {tc.currency}
                </div>
                <div style="display: flex; gap: 1.25rem; font-size: 0.95rem; color: #D1D5DB !important;">
                    <span>⭐ <b>{tc.interview_score or 4.5}</b>/5 ({tc.endorsements_count or 50}+ endorsements)</span>
                    <span>🎯 Skills Match: <b>{report.top_candidate.skills_match_pct}%</b></span>
                    <span>⚡ Fit Score: <b style="color: #34D399;">{tc_score}/100</b></span>
                </div>
            </div>
        </div>
        <div style="margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.15); color: #E5E7EB !important; line-height: 1.6; font-size: 1.02rem;">
            💡 {report.top_candidate_reasoning}
        </div>
        <div style="margin-top: 1.25rem; text-align: right;">
            <a href="{tc.profile_url}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white !important; padding: 0.6rem 1.4rem; border-radius: 10px; font-weight: 700; text-decoration: none; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);">
                📇 View Full Profile on {tc.source} ↗
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Runner Up Card
    if report.runner_up_candidate:
        ru = report.runner_up_candidate.candidate
        ru_score = report.runner_up_candidate.fit_score

        with st.container():
            st.markdown(f"""
            <div class="card-box" style="border-left: 4px solid #6366F1;">
                <div class="best-pick-header">
                    <span class="badge-runner-up">🥈 Runner-Up Candidate</span>
                    <span class="store-tag">Source: {ru.source}</span>
                </div>
                <div style="display: flex; gap: 1.25rem; flex-wrap: wrap; align-items: center;">
                    <div style="flex: 1; min-width: 250px;">
                        <h3 style="margin: 0 0 0.4rem 0; color: #FFFFFF !important; font-size: 1.2rem;">{ru.name}</h3>
                        <div style="font-size: 1.4rem; font-weight: 700; color: #818CF8 !important;">
                            {ru.expected_salary:,.2f} {ru.currency}
                        </div>
                        <div style="font-size: 0.95rem; color: #9CA3AF !important; margin-top: 0.25rem;">
                            Score: <b>{ru_score}/100</b> | Interview: <b>{ru.interview_score or 4.2}</b> ⭐
                        </div>
                    </div>
                    <div>
                        <a href="{ru.profile_url}" target="_blank" style="display: inline-block; background-color: #312E81; color: #E0E7FF !important; padding: 0.5rem 1.2rem; border-radius: 8px; font-weight: 600; text-decoration: none; border: 1px solid #4338CA;">
                            Contact Candidate ↗
                        </a>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
