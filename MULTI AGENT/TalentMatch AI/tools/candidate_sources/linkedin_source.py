import requests
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
import re

from tools.candidate_sources.base_source import BaseCandidateSource
from models.schemas import RawCandidate

class LinkedInSource(BaseCandidateSource):
    def __init__(self):
        super().__init__(source_name="LinkedIn", domain="linkedin.com")

    def scrape(self, job_title: str, max_results: int = 5) -> List[RawCandidate]:
        """Attempt to query LinkedIn public search via HTTP request, falling back gracefully.

        LinkedIn requires an authenticated session for real profile search results, so this
        almost always falls through to the resilient mock generator below — mirrored here for
        architectural parity with the other sourcing channels.
        """
        candidates: List[RawCandidate] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        url = f"https://www.linkedin.com/pub/dir?q={requests.utils.quote(job_title)}"

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.select('li.profile-result')

                for item in items[:max_results]:
                    name_elem = item.select_one('span.name')
                    link_elem = item.select_one('a')

                    if name_elem and link_elem:
                        name = name_elem.get_text(strip=True)
                        profile_url = link_elem.get('href', '')
                        candidates.append(
                            RawCandidate(
                                name=name,
                                currency="EGP",
                                profile_url=profile_url,
                                skills={"Source": "LinkedIn"},
                                source=self.source_name,
                                sourced_at=datetime.utcnow()
                            )
                        )
        except Exception:
            pass

        # LinkedIn blocks unauthenticated scraping (login wall / CAPTCHA), so fall back reliably
        if len(candidates) < 2:
            return self.generate_mock_fallback(job_title, count=max_results)

        return candidates
