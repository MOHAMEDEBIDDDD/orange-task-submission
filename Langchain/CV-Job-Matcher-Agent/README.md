# CV Job Matcher Agent

Upload a CV (PDF) and get it parsed, matched against live job postings, and rated — via two different agent architectures built with **LangChain**, **LangGraph**, **LangMem**, and **Streamlit**, with optional **LangSmith** tracing.

## What it does

1. Extracts text from an uploaded CV PDF.
2. Parses it into a structured profile (skills, experience, suitable roles).
3. Searches the live web (Tavily) for real job postings matching that profile.
4. Rates the CV (score, strengths, weaknesses, actionable suggestions).
5. Remembers candidate preferences across runs using LangMem long-term memory.

## Two implementations

| File | Architecture |
|---|---|
| `single_agent_app.py` | **One** ReAct agent (LangGraph `create_react_agent`) equipped with a job-search tool and LangMem memory tools. It handles parsing, searching, and rating itself in one reasoning loop. |
| `multi_agent_app.py` | **Multiple** specialized agents wired into a LangGraph `StateGraph` pipeline: a parser agent → a tool-using job-matcher agent (with its own memory access) → a rating agent, each with a narrow job. |

Both share `shared.py` for CV text extraction, Pydantic schemas, and LLM/tool/memory-store setup.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with:
- `OPENAI_API_KEY` — from platform.openai.com
- `TAVILY_API_KEY` — free tier at [tavily.com](https://tavily.com)
- LangSmith vars are optional (tracing only) — leave blank to skip.

## Usage

```bash
streamlit run single_agent_app.py
```

or

```bash
streamlit run multi_agent_app.py
```

Upload a CV PDF, click **Analyze**, and review the parsed profile, matched jobs, and CV rating.

## Notes

- LangMem memory here uses an in-process `InMemoryStore`, so it persists across analyses within one running session but resets when the app restarts. Swap in a persistent store (e.g. a database-backed one) for real cross-session memory.
- Job search quality depends on the Tavily results for whatever role/skills the agent searches — treat matches as a starting point, not a guarantee.
