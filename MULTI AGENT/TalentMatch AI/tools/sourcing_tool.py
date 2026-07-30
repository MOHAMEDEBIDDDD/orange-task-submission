from typing import List
import yaml
from config.settings import settings
from models.schemas import RawCandidate
from tools.candidate_sources.linkedin_source import LinkedInSource
from tools.candidate_sources.indeed_source import IndeedSource
from tools.candidate_sources.wuzzuf_source import WuzzufSource
from tools.candidate_sources.internal_referrals_source import InternalReferralsSource
from tools.candidate_sources.company_careers_source import CompanyCareersSource

SOURCE_MAP = {
    "LinkedInSource": LinkedInSource,
    "IndeedSource": IndeedSource,
    "WuzzufSource": WuzzufSource,
    "InternalReferralsSource": InternalReferralsSource,
    "CompanyCareersSource": CompanyCareersSource,
}

def get_source_for_channel(source_name: str):
    """Instantiate the registered candidate source for a given channel name."""
    try:
        with open(settings.sources_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        for source in config.get("sources", []):
            if source.get("name").lower() == source_name.lower():
                cls_name = source.get("source_class")
                if cls_name in SOURCE_MAP:
                    return SOURCE_MAP[cls_name]()
    except Exception:
        pass

    # Fallback by matching source name directly
    if "linkedin" in source_name.lower():
        return LinkedInSource()
    elif "indeed" in source_name.lower():
        return IndeedSource()
    elif "wuzzuf" in source_name.lower():
        return WuzzufSource()
    elif "referral" in source_name.lower():
        return InternalReferralsSource()
    elif "career" in source_name.lower():
        return CompanyCareersSource()

    return LinkedInSource()

def execute_source_search(source_name: str, job_title: str, max_results: int = 5) -> List[RawCandidate]:
    """Execute a candidate source with error handling, returning raw candidates."""
    source = get_source_for_channel(source_name)
    try:
        return source.scrape(job_title, max_results=max_results)
    except Exception:
        # Fallback to prevent sourcing failure from breaking the pipeline
        return source.generate_mock_fallback(job_title, count=max_results)
