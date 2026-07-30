"""Shared schemas, CV parsing, and LLM/tool/memory setup used by both agent apps."""

from pypdf import PdfReader
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.store.memory import InMemoryStore

MEMORY_NAMESPACE = ("cv_job_matcher", "preferences")


class CVProfile(BaseModel):
    name: str = Field(description="Candidate's full name, or 'Unknown' if not found")
    summary: str = Field(description="2-3 sentence professional summary")
    skills: list[str] = Field(description="Key technical and soft skills")
    job_titles: list[str] = Field(description="Job titles/roles this candidate is qualified for")
    years_experience: float = Field(description="Estimated total years of professional experience")
    education: list[str] = Field(description="Degrees/certifications, e.g. 'BSc Computer Science, XYZ University'")


class JobMatch(BaseModel):
    title: str = Field(description="Job title")
    company: str = Field(description="Company name, or 'Unknown' if not found")
    location: str = Field(description="Job location, or 'Not specified'")
    url: str = Field(description="Link to the job posting")
    match_score: int = Field(description="0-100 how well this job matches the CV", ge=0, le=100)
    why_match: str = Field(description="1-2 sentence explanation of the match")


class JobMatches(BaseModel):
    jobs: list[JobMatch]


class CVRating(BaseModel):
    overall_score: int = Field(description="0-100 overall CV quality score", ge=0, le=100)
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str] = Field(description="Concrete, actionable suggestions to improve the CV")


def extract_text_from_pdf(file) -> str:
    reader = PdfReader(file)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return text.strip()


def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)


def get_search_tool() -> TavilySearch:
    return TavilySearch(
        max_results=5,
        name="search_jobs",
        description="Search the web for current, real job postings matching a role or set of skills.",
    )


def get_memory_store() -> InMemoryStore:
    return InMemoryStore(index={"embed": "openai:text-embedding-3-small", "dims": 1536})
