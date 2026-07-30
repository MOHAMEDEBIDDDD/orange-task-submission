from typing import List
from tools.candidate_sources.base_source import BaseCandidateSource
from models.schemas import RawCandidate

class InternalReferralsSource(BaseCandidateSource):
    def __init__(self):
        super().__init__(source_name="Internal Referrals", domain="internal.talentmatch.ai")

    def scrape(self, job_title: str, max_results: int = 5) -> List[RawCandidate]:
        """Source or generate realistic results from the internal employee-referral pool."""
        return self.generate_mock_fallback(job_title, count=max_results)
