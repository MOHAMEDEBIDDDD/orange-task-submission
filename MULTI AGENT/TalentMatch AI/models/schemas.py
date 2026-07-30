from typing import List, Dict, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field

class JobRequisition(BaseModel):
    job_title: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    must_have_skills: List[str] = Field(default_factory=list)
    priority: Literal["salary", "experience_rating", "fast_hire", "balanced"] = "balanced"
    selected_sources: List[str] = Field(default_factory=list)
    currency: str = "EGP"

class RawCandidate(BaseModel):
    name: str
    expected_salary: Optional[float] = None
    currency: str = "EGP"
    interview_score: Optional[float] = None
    endorsements_count: Optional[int] = None
    profile_url: str
    avatar_url: Optional[str] = None
    skills: Dict[str, str] = Field(default_factory=dict)
    source: str
    notice_period: Optional[str] = None
    sourced_at: datetime = Field(default_factory=datetime.utcnow)

class CleanCandidate(RawCandidate):
    candidate_id: str
    matched_profiles: List[str] = Field(default_factory=list)

class ReferenceInsight(BaseModel):
    candidate_id: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    verification_status: Literal["verified", "caution", "insufficient_data"] = "insufficient_data"
    verification_notes: Optional[str] = None

class ScoredCandidate(BaseModel):
    candidate: CleanCandidate
    reference_insight: Optional[ReferenceInsight] = None
    fit_score: float
    skills_match_pct: float
    within_salary_range: bool

class HiringReport(BaseModel):
    top_candidate: ScoredCandidate
    top_candidate_reasoning: str
    runner_up_candidate: Optional[ScoredCandidate] = None
    runner_up_reasoning: Optional[str] = None
    all_scored_candidates: List[ScoredCandidate] = Field(default_factory=list)
    rejected_summary: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
