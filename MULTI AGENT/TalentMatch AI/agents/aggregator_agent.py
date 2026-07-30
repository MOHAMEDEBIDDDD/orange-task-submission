from crewai import Agent

def create_aggregator_agent() -> Agent:
    """Create Candidate Deduplication & Aggregation Specialist Agent."""
    return Agent(
        role="Candidate Deduplication & Aggregation Specialist",
        goal="Merge all raw candidate profiles from every source into a single clean, deduplicated list, matching profiles that refer to the same real-world candidate even when named or formatted differently.",
        backstory="You are meticulous about data quality. You recognize when different profiles represent the exact same candidate across channels and merge them, never letting duplicate or low-quality profiles pollute the final shortlist.",
        verbose=True,
        allow_delegation=False
    )
