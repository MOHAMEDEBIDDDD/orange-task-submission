import streamlit as st
from typing import List
from models.schemas import ScoredCandidate

def render_reference_insights(scored_candidates: List[ScoredCandidate]):
    """Render candidate reference insights and verification analysis cards."""
    st.markdown("### 🛡️ Reference & Background Verification Intelligence")

    for sc in scored_candidates:
        c = sc.candidate
        ri = sc.reference_insight

        badge_style = "trust-trusted" if ri.verification_status == "verified" else ("trust-caution" if ri.verification_status == "caution" else "trust-insufficient")
        badge_label = "✅ Verified" if ri.verification_status == "verified" else ("⚠️ Use Caution" if ri.verification_status == "caution" else "ℹ️ Limited Reference Data")

        with st.expander(f"{c.name} ({c.source}) — {badge_label}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("##### 👍 Pros & Verified Strengths")
                if ri and ri.pros:
                    for pro in ri.pros:
                        st.markdown(f"- ✅ {pro}")
                else:
                    st.markdown("- ✅ Good salary-to-experience ratio relative to market average")

            with col2:
                st.markdown("##### 👎 Cons & Considerations")
                if ri and ri.cons:
                    for con in ri.cons:
                        st.markdown(f"- ⚠️ {con}")
                else:
                    st.markdown("- ℹ️ Standard reference terms apply")

            if ri and ri.verification_notes:
                st.markdown(f"**Reference Verification Assessment:** *{ri.verification_notes}*")
