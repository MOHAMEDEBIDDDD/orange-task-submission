import requests
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
import re

from tools.candidate_sources.base_source import BaseCandidateSource
from models.schemas import RawCandidate

class IndeedSource(BaseCandidateSource):
    def __init__(self):
        super().__init__(source_name="Indeed", domain="indeed.com")

    def scrape(self, job_title: str, max_results: int = 5) -> List[RawCandidate]:
        """Attempt scraping Indeed resume search via HTTP request, falling back gracefully."""
        candidates: List[RawCandidate] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        url = f"https://www.indeed.com/resumes?q={requests.utils.quote(job_title)}"

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.select('div.resume-card')

                for item in items[:max_results]:
                    name_elem = item.select_one('a.app-link')

                    if name_elem:
                        name = name_elem.get_text(strip=True)
                        candidates.append(
                            RawCandidate(
                                name=name,
                                currency="EGP",
                                profile_url=f"https://www.indeed.com{name_elem.get('href', '')}",
                                skills={"Source": "Indeed"},
                                source=self.source_name,
                                sourced_at=datetime.utcnow()
                            )
                        )
        except Exception:
            pass

        if len(candidates) < 2:
            return self.generate_mock_fallback(job_title, count=max_results)

        return candidates
