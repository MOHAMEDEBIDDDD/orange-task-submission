from typing import List
from tools.candidate_sources.base_source import BaseCandidateSource
from models.schemas import RawCandidate

class CompanyCareersSource(BaseCandidateSource):
    def __init__(self):
        super().__init__(source_name="Company Careers", domain="careers.company.com")

    def scrape(self, job_title: str, max_results: int = 5) -> List[RawCandidate]:
        """Source or generate realistic results from the company's own careers page applicants."""
        return self.generate_mock_fallback(job_title, count=max_results)
