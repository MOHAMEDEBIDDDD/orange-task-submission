"""CV Job Matcher — single ReAct agent (LangGraph) with a job-search tool and LangMem memory."""

import json

import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langmem import create_manage_memory_tool, create_search_memory_tool

from shared import MEMORY_NAMESPACE, extract_text_from_pdf, get_llm, get_memory_store, get_search_tool

load_dotenv(override=True)

SYSTEM_PROMPT = """You are a career-advisor agent. Given a candidate's CV text, you will:

1. Extract the candidate's key skills, experience level, and suitable job titles.
2. Use the `search_jobs` tool to find 3-5 real, currently open job postings that match the
   candidate's strongest skills/role. Search with a specific, targeted query.
3. Rate the CV out of 100 on clarity, impact, and relevance, with concrete strengths,
   weaknesses, and improvement suggestions.
4. Before searching, use your memory tools to recall any previously saved candidate
   preferences (e.g. preferred location, remote work, target role). Save any new
   preferences you learn from this CV for next time.

Respond with ONLY a single JSON object (no markdown fences, no extra text) with this
exact structure:
{
  "profile": {"name": str, "summary": str, "skills": [str], "job_titles": [str],
              "years_experience": number, "education": [str]},
  "job_matches": [{"title": str, "company": str, "location": str, "url": str,
                    "match_score": number, "why_match": str}],
  "rating": {"overall_score": number, "strengths": [str], "weaknesses": [str],
             "suggestions": [str]}
}
"""


@st.cache_resource
def build_agent():
    store = get_memory_store()
    tools = [
        get_search_tool(),
        create_manage_memory_tool(namespace=MEMORY_NAMESPACE),
        create_search_memory_tool(namespace=MEMORY_NAMESPACE),
    ]
    return create_agent(get_llm(), tools=tools, store=store, system_prompt=SYSTEM_PROMPT)


def parse_json_response(content: str):
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def render_results(data: dict):
    profile = data.get("profile", {})
    jobs = data.get("job_matches", [])
    rating = data.get("rating", {})

    st.subheader("Profile")
    st.write(f"**{profile.get('name', 'Unknown')}** — {profile.get('years_experience', '?')} yrs experience")
    st.write(profile.get("summary", ""))
    st.write("**Skills:** " + ", ".join(profile.get("skills", [])))
    st.write("**Suitable roles:** " + ", ".join(profile.get("job_titles", [])))

    st.subheader("Matching jobs")
    if not jobs:
        st.info("No job matches returned.")
    for job in jobs:
        with st.container(border=True):
            st.markdown(f"**[{job.get('title', 'Untitled')}]({job.get('url', '#')})** — "
                        f"{job.get('company', 'Unknown')} ({job.get('location', 'Not specified')})")
            st.progress(max(0, min(100, job.get("match_score", 0))) / 100)
            st.caption(job.get("why_match", ""))

    st.subheader("CV rating")
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


st.set_page_config(page_title="CV Job Matcher — Single Agent", page_icon="🧑‍💼", layout="wide")
st.title("🧑‍💼 CV Job Matcher — Single Agent")
st.caption("One ReAct agent (LangGraph + LangChain) with a job-search tool and long-term memory (LangMem).")

uploaded = st.file_uploader("Upload your CV (PDF)", type=["pdf"])

if uploaded and st.button("Analyze CV", type="primary"):
    with st.spinner("Reading CV and running the agent (this can take a minute)..."):
        cv_text = extract_text_from_pdf(uploaded)
        if not cv_text:
            st.error("Couldn't extract any text from that PDF.")
            st.stop()

        agent = build_agent()
        result = agent.invoke({"messages": [{"role": "user", "content": f"Here is my CV:\n\n{cv_text}"}]})
        final_message = result["messages"][-1].content
        data = parse_json_response(final_message)

    if data is None:
        st.warning("Couldn't parse structured output — showing the raw agent response instead.")
        st.markdown(final_message)
    else:
        render_results(data)
