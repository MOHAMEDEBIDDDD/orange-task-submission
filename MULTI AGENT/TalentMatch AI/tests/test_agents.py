import pytest
from agents.job_requisition_agent import create_job_requisition_agent
from agents.sourcing_agents import create_sourcing_agent_for_source
from agents.aggregator_agent import create_aggregator_agent
from agents.reference_check_agent import create_reference_check_agent
from agents.fit_scoring_agent import create_fit_scoring_agent
from agents.report_agent import create_report_agent

def test_agent_initialization():
    req_agent = create_job_requisition_agent()
    assert req_agent.role == "Senior Talent Acquisition Analyst"

    sourcing_agent = create_sourcing_agent_for_source("LinkedIn")
    assert "LinkedIn" in sourcing_agent.role

    agg_agent = create_aggregator_agent()
    assert agg_agent.role == "Candidate Deduplication & Aggregation Specialist"

    reference_agent = create_reference_check_agent()
    assert reference_agent.role == "Candidate Reference & Background Verification Analyst"

    fit_agent = create_fit_scoring_agent()
    assert fit_agent.role == "Candidate Fit & Scoring Specialist"

    report_agent = create_report_agent()
    assert report_agent.role == "Chief Talent Recommendation Writer"
