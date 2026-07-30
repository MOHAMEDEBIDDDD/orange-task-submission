import pytest
from datetime import datetime
from models.schemas import RawCandidate, JobRequisition
from utils.fit_score import calculate_fit_score, compute_salary_score, calculate_skills_match_pct

def test_salary_score_calculation():
    assert compute_salary_score(30000.0, 30000.0, 60000.0) == 100.0
    assert compute_salary_score(60000.0, 30000.0, 60000.0) == 0.0
    assert compute_salary_score(45000.0, 30000.0, 60000.0) == 50.0

def test_skills_match_pct():
    pct = calculate_skills_match_pct("Senior Python Engineer AWS", {}, ["Python", "AWS"])
    assert pct == 100.0

    pct_partial = calculate_skills_match_pct("Junior Java Developer", {}, ["Python", "AWS"])
    assert pct_partial == 0.0

def test_fit_score_priority():
    candidate = RawCandidate(
        name="Test Candidate",
        expected_salary=30000.0,
        currency="EGP",
        interview_score=4.5,
        endorsements_count=100,
        profile_url="http://test.com",
        source="TestChannel",
        sourced_at=datetime.utcnow()
    )

    reqs_salary = JobRequisition(
        job_title="Test Role",
        priority="salary",
        selected_sources=["TestChannel"]
    )

    score, match_pct, in_range = calculate_fit_score(candidate, reqs_salary, min_salary=30000.0, max_salary=60000.0)
    assert score > 0
    assert match_pct == 100.0
    assert in_range is True
