import streamlit as st

def render_progress(stage: str, progress: float):
    """Render live multi-agent execution progress status bar."""
    st.progress(progress)
    st.info(f"🤖 **Multi-Agent Recruiting Pipeline Status:** {stage}")
