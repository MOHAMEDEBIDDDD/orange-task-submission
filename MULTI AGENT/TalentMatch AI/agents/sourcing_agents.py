from crewai import Agent
from tools.serper_search_tool import serper_search_tool

def create_sourcing_agent_for_source(source_name: str) -> Agent:
    """Dynamically create a sourcing agent bound to a specific candidate channel."""
    return Agent(
        role=f"{source_name} Candidate Sourcing Specialist",
        goal=f"Find and extract accurate, up-to-date candidate profiles matching the job requisition from {source_name} only.",
        backstory=f"You are a specialist sourcing agent focused exclusively on {source_name}. You know how to find the most relevant candidate profiles and extract clean structured data from them, ignoring irrelevant or unqualified profiles.",
        tools=[serper_search_tool],
        verbose=True,
        allow_delegation=False
    )
