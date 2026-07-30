import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from config.settings import settings
from db.database import get_db
from db.models import RequisitionCache, SalaryHistory, HiringSearchHistory
from models.schemas import JobRequisition, HiringReport, CleanCandidate

def generate_query_hash(requisition: JobRequisition) -> str:
    """Generate MD5 hash representing job requisition and filters for cache key lookup."""
    raw_str = (
        f"{requisition.job_title.strip().lower()}_"
        f"{requisition.salary_min}_{requisition.salary_max}_"
        f"{','.join(sorted(requisition.must_have_skills))}_"
        f"{requisition.priority}_"
        f"{','.join(sorted(requisition.selected_sources))}"
    )
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()

def get_cached_results(query_hash: str) -> Optional[HiringReport]:
    """Retrieve non-expired HiringReport from RequisitionCache if present."""
    try:
        with get_db() as db:
            cached_entry = db.query(RequisitionCache).filter(
                RequisitionCache.query_hash == query_hash,
                RequisitionCache.expires_at > datetime.utcnow()
            ).first()

            if cached_entry:
                report_dict = json.loads(cached_entry.results_json)
                return HiringReport.model_validate(report_dict)
    except Exception:
        pass
    return None

def save_to_cache(query_hash: str, requisition: JobRequisition, report: HiringReport):
    """Save HiringReport to RequisitionCache table."""
    try:
        expires = datetime.utcnow() + timedelta(hours=settings.cache_ttl_hours)
        report_json = json.dumps(report.model_dump(mode='json'))

        with get_db() as db:
            # Remove any existing cache entry for hash
            db.query(RequisitionCache).filter(RequisitionCache.query_hash == query_hash).delete()

            new_cache = RequisitionCache(
                query_hash=query_hash,
                job_title=requisition.job_title,
                results_json=report_json,
                expires_at=expires
            )
            db.add(new_cache)
    except Exception:
        pass

def log_salary_history(candidates: List[CleanCandidate]):
    """Record sourced candidate expected salaries to SalaryHistory table."""
    try:
        with get_db() as db:
            for c in candidates:
                if c.expected_salary is not None:
                    sh = SalaryHistory(
                        candidate_id=c.candidate_id,
                        candidate_name=c.name,
                        source=c.source,
                        expected_salary=c.expected_salary,
                        currency=c.currency,
                        recorded_at=datetime.utcnow()
                    )
                    db.add(sh)
    except Exception:
        pass

def log_search_history(requisition: JobRequisition, report: HiringReport):
    """Record hiring search event summary into HiringSearchHistory table."""
    try:
        filters = {
            "salary_min": requisition.salary_min,
            "salary_max": requisition.salary_max,
            "must_haves": requisition.must_have_skills,
            "priority": requisition.priority,
            "sources": requisition.selected_sources
        }

        top_name = report.top_candidate.candidate.name if report.top_candidate else "N/A"
        top_salary = report.top_candidate.candidate.expected_salary if report.top_candidate else None

        with get_db() as db:
            sh = HiringSearchHistory(
                job_title=requisition.job_title,
                filters_json=json.dumps(filters),
                top_candidate_name=top_name,
                top_candidate_salary=top_salary,
                searched_at=datetime.utcnow()
            )
            db.add(sh)
    except Exception:
        pass

def get_all_search_history() -> List[Dict]:
    """Retrieve hiring search history records for UI display."""
    try:
        with get_db() as db:
            records = db.query(HiringSearchHistory).order_by(HiringSearchHistory.searched_at.desc()).limit(20).all()
            return [
                {
                    "id": r.id,
                    "job_title": r.job_title,
                    "filters_json": r.filters_json,
                    "top_candidate_name": r.top_candidate_name,
                    "top_candidate_salary": r.top_candidate_salary,
                    "searched_at": r.searched_at.strftime("%Y-%m-%d %H:%M")
                }
                for r in records
            ]
    except Exception:
        return []

def get_salary_history_records() -> List[Dict]:
    """Retrieve recorded salary history points for charting."""
    try:
        with get_db() as db:
            records = db.query(SalaryHistory).order_by(SalaryHistory.recorded_at.asc()).all()
            return [
                {
                    "candidate_id": r.candidate_id,
                    "candidate_name": r.candidate_name,
                    "source": r.source,
                    "expected_salary": r.expected_salary,
                    "currency": r.currency,
                    "recorded_at": r.recorded_at.strftime("%Y-%m-%d %H:%M")
                }
                for r in records
            ]
    except Exception:
        return []
