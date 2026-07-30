from crewai import Agent

def create_reference_check_agent() -> Agent:
    """Create Candidate Reference & Background Verification Analyst Agent."""
    return Agent(
        role="Candidate Reference & Background Verification Analyst",
        goal="Analyze available profile signals and endorsements for each candidate to extract genuine strengths and concerns, and flag any candidate with insufficient or suspicious verification data.",
        backstory="You have deep experience vetting references and detecting inflated or fabricated credentials, extracting genuinely useful insights from authentic candidate history.",
        verbose=True,
        allow_delegation=False
    )
