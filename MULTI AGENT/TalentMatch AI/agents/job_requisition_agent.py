from crewai import Agent
from config.settings import settings

def create_job_requisition_agent() -> Agent:
    """Create Job Requisition Analyst Agent."""
    return Agent(
        role="Senior Talent Acquisition Analyst",
        goal="Transform the hiring manager's raw role request and preferences into a precise, structured job requisition that captures explicit and implicit hiring needs.",
        backstory="You are an expert talent acquisition consultant with 15 years of experience translating vague hiring requests into precise role specifications. You always think about what the team truly needs, not just the job title they typed.",
        verbose=True,
        allow_delegation=False
    )
