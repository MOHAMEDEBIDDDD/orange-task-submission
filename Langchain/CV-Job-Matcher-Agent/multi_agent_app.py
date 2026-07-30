"""CV Job Matcher — multi-agent LangGraph pipeline.

Three specialized agents wired into a StateGraph:
  parser_agent   -> structured extraction of the CV into a profile
  job_matcher    -> a tool-using ReAct agent that searches for and scores job matches,
                    with LangMem access to recall/save candidate preferences
  rating_agent   -> structured CV rating (score, strengths, weaknesses, suggestions)
"""

from typing import TypedDict

import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langgraph.graph import END, START, StateGraph
from langmem import create_manage_memory_tool, create_search_memory_tool

from shared import (
    MEMORY_NAMESPACE,
    CVProfile,
    CVRating,
    JobMatches,
    extract_text_from_pdf,
    get_llm,
    get_memory_store,
    get_search_tool,
)

load_dotenv(override=True)


class PipelineState(TypedDict):
    cv_text: str
    profile: dict
    job_matches: list
    rating: dict


def make_parser_node():
    llm = get_llm().with_structured_output(CVProfile)

    def parser_agent(state: PipelineState) -> dict:
        profile = llm.invoke(
            "Extract a structured profile from this CV.\n\n" + state["cv_text"]
        )
        return {"profile": profile.model_dump()}

    return parser_agent


def make_job_matcher_node(store):
    search_agent = create_agent(
        get_llm(),
        tools=[
            get_search_tool(),
            create_manage_memory_tool(namespace=MEMORY_NAMESPACE),
            create_search_memory_tool(namespace=MEMORY_NAMESPACE),
        ],
        store=store,
        system_prompt=(
            "You are a job-search agent. Given a candidate profile, recall any saved "
            "preferences (location, remote work, target role), then use the `search_jobs` "
            "tool to find 3-5 real, currently open job postings matching the candidate's "
            "skills and titles. Save any new preferences you learn. Once you have enough "
            "results, stop calling tools and summarize the matches in your final answer."
        ),
        response_format=JobMatches,
    )

    def job_matcher(state: PipelineState) -> dict:
        profile = state["profile"]
        query = (
            f"Candidate profile:\nSkills: {', '.join(profile.get('skills', []))}\n"
            f"Suitable roles: {', '.join(profile.get('job_titles', []))}\n"
            f"Years of experience: {profile.get('years_experience')}\n"
            "Find matching job postings for this candidate."
        )
        result = search_agent.invoke({"messages": [{"role": "user", "content": query}]})
        matches: JobMatches = result["structured_response"]
        return {"job_matches": [m.model_dump() for m in matches.jobs]}

    return job_matcher


def make_rating_node():
    llm = get_llm().with_structured_output(CVRating)

    def rating_agent(state: PipelineState) -> dict:
        rating = llm.invoke(
            "Rate this CV out of 100 on clarity, impact, and relevance. Give concrete "
            "strengths, weaknesses, and actionable suggestions.\n\n" + state["cv_text"]
        )
        return {"rating": rating.model_dump()}

    return rating_agent


@st.cache_resource
def build_graph():
    store = get_memory_store()
    graph = StateGraph(PipelineState)
    graph.add_node("parser_agent", make_parser_node())
    graph.add_node("job_matcher", make_job_matcher_node(store))
    graph.add_node("rating_agent", make_rating_node())
    graph.add_edge(START, "parser_agent")
    graph.add_edge("parser_agent", "job_matcher")
    graph.add_edge("job_matcher", "rating_agent")
    graph.add_edge("rating_agent", END)
    return graph.compile(store=store)


def render_results(state: dict):
    profile = state.get("profile", {})
    jobs = state.get("job_matches", [])
    rating = state.get("rating", {})

    st.subheader("Profile — parser agent")
    st.write(f"**{profile.get('name', 'Unknown')}** — {profile.get('years_experience', '?')} yrs experience")
    st.write(profile.get("summary", ""))
    st.write("**Skills:** " + ", ".join(profile.get("skills", [])))
    st.write("**Suitable roles:** " + ", ".join(profile.get("job_titles", [])))

    st.subheader("Matching jobs — job-matcher agent")
    if not jobs:
        st.info("No job matches returned.")
    for job in jobs:
        with st.container(border=True):
            st.markdown(f"**[{job.get('title', 'Untitled')}]({job.get('url', '#')})** — "
                        f"{job.get('company', 'Unknown')} ({job.get('location', 'Not specified')})")
            st.progress(max(0, min(100, job.get("match_score", 0))) / 100)
            st.caption(job.get("why_match", ""))

    st.subheader("CV rating — rating agent")
    st.metric("Overall score", f"{rating.get('overall_score', '?')}/100")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Strengths**")
        for s in rating.get("strengths", []):
            st.markdown(f"- {s}")
    with col2:
        st.markdown("**Weaknesses**")
        for w in rating.get("weaknesses", []):
            st.markdown(f"- {w}")
    with col3:
        st.markdown("**Suggestions**")
        for sug in rating.get("suggestions", []):
            st.markdown(f"- {sug}")


st.set_page_config(page_title="CV Job Matcher — Multi-Agent", page_icon="🧑‍💼", layout="wide")
st.title("🧑‍💼 CV Job Matcher — Multi-Agent Pipeline")
st.caption(
    "A LangGraph pipeline of three specialized agents: parser → job-matcher (with search "
    "tool + LangMem memory) → rating."
)

uploaded = st.file_uploader("Upload your CV (PDF)", type=["pdf"])

if uploaded and st.button("Analyze CV", type="primary"):
    with st.spinner("Reading CV and running the agent pipeline (this can take a minute)..."):
        cv_text = extract_text_from_pdf(uploaded)
        if not cv_text:
            st.error("Couldn't extract any text from that PDF.")
            st.stop()

        graph = build_graph()
        final_state = graph.invoke({"cv_text": cv_text})

    render_results(final_state)
