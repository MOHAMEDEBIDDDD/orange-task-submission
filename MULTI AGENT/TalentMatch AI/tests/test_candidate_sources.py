import pytest
from tools.candidate_sources.linkedin_source import LinkedInSource
from tools.candidate_sources.wuzzuf_source import WuzzufSource
from tools.sourcing_tool import execute_source_search
from utils.candidate_matcher import deduplicate_candidates

def test_source_fallback_reliability():
    linkedin = LinkedInSource()
    results = linkedin.scrape("Senior Backend Engineer", max_results=3)
    assert len(results) >= 1
    assert results[0].source == "LinkedIn"

def test_deduplication():
    wuzzuf = WuzzufSource()
    results_wuzzuf = wuzzuf.scrape("Senior Backend Engineer", max_results=3)
    clean = deduplicate_candidates(results_wuzzuf)
    assert len(clean) >= 1
    assert hasattr(clean[0], "candidate_id")
