from typing import Tuple, List, Optional
from models.schemas import RawCandidate, JobRequisition, ReferenceInsight

def calculate_skills_match_pct(candidate_name: str, candidate_skills: dict, must_have_skills: List[str]) -> float:
    """Calculate percentage of must-have skills present in the candidate's name/profile or skills dictionary."""
    if not must_have_skills:
        return 100.0

    matched = 0
    search_text = (candidate_name + " " + " ".join(f"{k} {v}" for k, v in candidate_skills.items())).lower()

    for skill in must_have_skills:
        skill_clean = skill.strip().lower()
        if skill_clean in search_text:
            matched += 1

    return round((matched / len(must_have_skills)) * 100.0, 1)

def compute_salary_score(salary: Optional[float], min_salary: float, max_salary: float) -> float:
    """Inversely normalize expected salary relative to min and max salaries found (0-100 scale)."""
    if salary is None:
        return 50.0
    if max_salary <= min_salary or max_salary == 0:
        return 100.0

    # Lower expected salary is better (higher score)
    score = 100.0 * (1.0 - ((salary - min_salary) / (max_salary - min_salary)))
    return round(max(0.0, min(100.0, score)), 1)

def calculate_fit_score(
    candidate: RawCandidate,
    requisition: JobRequisition,
    min_salary: float,
    max_salary: float,
    reference_insight: Optional[ReferenceInsight] = None
) -> Tuple[float, float, bool]:
    """
    Calculate (fit_score, skills_match_pct, within_salary_range).

    fit_score is a 0-100 float computed from weighted criteria:
    - salary_score
    - interview_score
    - skills_match_pct
    - trust_score
    """
    # 1. Weights based on hiring manager priority
    priority = requisition.priority
    if priority == "salary":
        w_salary, w_interview, w_skills, w_trust = 0.5, 0.2, 0.2, 0.1
    elif priority == "experience_rating":
        w_salary, w_interview, w_skills, w_trust = 0.2, 0.4, 0.2, 0.2
    else:  # balanced or fast_hire
        w_salary, w_interview, w_skills, w_trust = 0.25, 0.25, 0.25, 0.25

    # 2. Component scores
    salary_score = compute_salary_score(candidate.expected_salary, min_salary, max_salary)

    # Interview score (0-100)
    interview_score = candidate.interview_score if candidate.interview_score is not None else 3.5
    interview_score_pct = min(100.0, max(0.0, (interview_score / 5.0) * 100.0))

    # Skills match percentage
    skills_match_pct = calculate_skills_match_pct(
        candidate.name, candidate.skills, requisition.must_have_skills
    )

    # Trust score
    if reference_insight:
        if reference_insight.verification_status == "verified":
            trust_score = 100.0
        elif reference_insight.verification_status == "caution":
            trust_score = 40.0
        else:
            trust_score = 70.0
    else:
        trust_score = 70.0

    # 3. Weighted total
    fit_score = (
        salary_score * w_salary +
        interview_score_pct * w_interview +
        skills_match_pct * w_skills +
        trust_score * w_trust
    )

    # 4. Within salary range check
    within_salary_range = True
    if candidate.expected_salary is not None:
        if requisition.salary_min is not None and candidate.expected_salary < requisition.salary_min:
            within_salary_range = False
        if requisition.salary_max is not None and candidate.expected_salary > requisition.salary_max:
            within_salary_range = False

    return round(fit_score, 1), skills_match_pct, within_salary_range
