import re
import hashlib
from typing import List, Dict
from rapidfuzz import fuzz
from models.schemas import RawCandidate, CleanCandidate

def normalize_name(name: str) -> str:
    """Clean candidate name by lowercasing, removing special characters, and extra whitespaces."""
    cleaned = re.sub(r'[^\w\s]', ' ', name.lower())
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def generate_candidate_id(canonical_name: str) -> str:
    """Generate a deterministic hashed ID for a canonical candidate name."""
    return hashlib.md5(canonical_name.encode('utf-8')).hexdigest()[:12]

def deduplicate_candidates(raw_candidates: List[RawCandidate], similarity_threshold: float = 85.0) -> List[CleanCandidate]:
    """
    Group similar raw candidate profiles from different sources into CleanCandidate instances.
    If similarity between normalized names > threshold, merge profiles.
    """
    if not raw_candidates:
        return []

    clusters: List[Dict] = []  # list of dicts: {'canonical': RawCandidate, 'profiles': [urls]}

    for item in raw_candidates:
        norm_name = normalize_name(item.name)
        matched_cluster = None

        for cluster in clusters:
            cluster_norm_name = normalize_name(cluster['canonical'].name)
            sim_score = fuzz.token_sort_ratio(norm_name, cluster_norm_name)

            if sim_score >= similarity_threshold:
                matched_cluster = cluster
                break

        if matched_cluster:
            # Add profile URL as matched profile
            matched_cluster['profiles'].append(item.profile_url)
            # Update canonical if new item has higher non-null interview score or better details
            if item.interview_score and (not matched_cluster['canonical'].interview_score or item.interview_score > matched_cluster['canonical'].interview_score):
                matched_cluster['canonical'] = item
        else:
            clusters.append({
                'canonical': item,
                'profiles': [item.profile_url]
            })

    clean_candidates: List[CleanCandidate] = []
    for cluster in clusters:
        cc = cluster['canonical']
        clean_name = normalize_name(cc.name)
        candidate_id = generate_candidate_id(clean_name)

        clean_candidates.append(
            CleanCandidate(
                name=cc.name,
                expected_salary=cc.expected_salary,
                currency=cc.currency,
                interview_score=cc.interview_score,
                endorsements_count=cc.endorsements_count,
                profile_url=cc.profile_url,
                avatar_url=cc.avatar_url,
                skills=cc.skills,
                source=cc.source,
                notice_period=cc.notice_period,
                sourced_at=cc.sourced_at,
                candidate_id=candidate_id,
                matched_profiles=cluster['profiles']
            )
        )

    return clean_candidates
