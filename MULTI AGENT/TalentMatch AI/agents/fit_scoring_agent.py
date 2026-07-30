from crewai import Agent

def create_fit_scoring_agent() -> Agent:
    """Create Candidate Fit & Scoring Specialist Agent."""
    return Agent(
        role="Candidate Fit & Scoring Specialist",
        goal="Score every clean candidate on a 0-100 Fit-for-Role scale using expected salary, skills match percentage, interview score, reference trust, and the hiring manager's stated priority.",
        backstory="You are a data-driven analyst who never lets a polished resume override objective scoring criteria. You rigorously calculate mathematical fit scores for every candidate.",
        verbose=True,
        allow_delegation=False
    )
