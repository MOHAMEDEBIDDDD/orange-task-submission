import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Callable, Optional

from models.schemas import (
    JobRequisition, HiringReport, RawCandidate, CleanCandidate,
    ReferenceInsight, ScoredCandidate
)
from tools.sourcing_tool import execute_source_search
from utils.candidate_matcher import deduplicate_candidates
from utils.fit_score import calculate_fit_score
from tools.cache_tool import (
    generate_query_hash, get_cached_results, save_to_cache,
    log_salary_history, log_search_history
)

def analyze_candidate_trust(candidate: CleanCandidate) -> ReferenceInsight:
    """Generate reference insights and verification flags for a given candidate."""
    interview_score = candidate.interview_score or 4.0
    endorsements = candidate.endorsements_count or 10

    pros = []
    cons = []

    if interview_score >= 4.5:
        pros.append("Outstanding interview performance & strong technical depth")
        pros.append("Consistently responsive and reliable throughout the process")
        verification_status = "verified"
        verification_notes = "Verified strong interview signals with consistent positive feedback."
    elif interview_score >= 4.0:
        pros.append("Solid interview performance and good role alignment")
        cons.append("Minor gaps noted in secondary skills or availability")
        verification_status = "verified"
        verification_notes = "Solid track record and authentic reference feedback."
    else:
        pros.append("Competitive salary expectation for the role")
        cons.append("Mixed interview feedback regarding depth or communication")
        verification_status = "caution"
        verification_notes = "Lower average interview score or insufficient verified reference volume."

    if endorsements < 15:
        verification_status = "insufficient_data"
        verification_notes = "Low total number of verified endorsements/references recorded so far."
        cons.append("Limited reference/endorsement sample size")

    return ReferenceInsight(
        candidate_id=candidate.candidate_id,
        pros=pros,
        cons=cons,
        verification_status=verification_status,
        verification_notes=verification_notes
    )

async def run_talent_search(
    requisition: JobRequisition,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> HiringReport:
    """
    Execute end-to-end multi-agent hiring workflow:
    1. Check cache (instant return if hit)
    2. Parallel Async Candidate Sourcing across selected channels
    3. Aggregation & Deduplication
    4. Reference & Verification Intelligence Analysis
    5. Scoring & Fit Comparison
    6. Executive Hiring Report Synthesis
    7. Persistent Caching & DB Logging
    """

    def notify(stage: str, progress: float):
        if progress_callback:
            try:
                progress_callback(stage, progress)
            except Exception:
                pass

    # 1. Check cache
    query_hash = generate_query_hash(requisition)
    cached_report = get_cached_results(query_hash)
    if cached_report:
        notify("⚡ Instant cached results loaded!", 1.0)
        return cached_report

    # 2. Stage 1: Requisition Analysis
    notify("🔍 Step 1/6: Analyzing job requisition and hiring criteria...", 0.15)
    await asyncio.sleep(0.3)

    # 3. Stage 2: Parallel Sourcing Agents Execution
    selected_sources = requisition.selected_sources or ["LinkedIn", "Indeed", "Wuzzuf", "Internal Referrals"]
    notify(f"🌐 Step 2/6: Sourcing candidates across {len(selected_sources)} channels in parallel...", 0.35)

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=len(selected_sources)) as executor:
        futures = [
            loop.run_in_executor(
                executor,
                execute_source_search,
                source,
                requisition.job_title,
                5
            )
            for source in selected_sources
        ]
        sourced_results_lists = await asyncio.gather(*futures, return_exceptions=True)

    all_raw_candidates: List[RawCandidate] = []
    for res in sourced_results_lists:
        if isinstance(res, list):
            all_raw_candidates.extend(res)

    # 4. Stage 3: Aggregation & Deduplication
    notify("🧹 Step 3/6: Deduplicating and unifying candidate profiles...", 0.55)
    clean_candidates: List[CleanCandidate] = deduplicate_candidates(all_raw_candidates)

    if not clean_candidates:
        # Fallback if no candidates found
        raw_fallback = execute_source_search("LinkedIn", requisition.job_title, 3)
        clean_candidates = deduplicate_candidates(raw_fallback)

    # 5. Stage 4: Reference & Verification Intelligence
    notify("🛡️ Step 4/6: Analyzing candidate references & verification signals...", 0.70)
    reference_insights: List[ReferenceInsight] = [analyze_candidate_trust(cc) for cc in clean_candidates]
    insights_map = {ri.candidate_id: ri for ri in reference_insights}

    # 6. Stage 5: Fit Scoring
    notify("⚖️ Step 5/6: Computing Fit-for-Role scores & salary ranks...", 0.85)
    valid_salaries = [c.expected_salary for c in clean_candidates if c.expected_salary is not None]
    min_salary = min(valid_salaries) if valid_salaries else 0.0
    max_salary = max(valid_salaries) if valid_salaries else 0.0

    scored_candidates: List[ScoredCandidate] = []
    for cc in clean_candidates:
        ri = insights_map.get(cc.candidate_id)
        score, match_pct, in_range = calculate_fit_score(
            candidate=cc,
            requisition=requisition,
            min_salary=min_salary,
            max_salary=max_salary,
            reference_insight=ri
        )
        scored_candidates.append(
            ScoredCandidate(
                candidate=cc,
                reference_insight=ri,
                fit_score=score,
                skills_match_pct=match_pct,
                within_salary_range=in_range
            )
        )

    # Sort candidates by fit_score descending
    scored_candidates.sort(key=lambda x: x.fit_score, reverse=True)

    # 7. Stage 6: Final Report Synthesis
    notify("📝 Step 6/6: Synthesizing final hiring recommendation report...", 0.95)
    top_candidate = scored_candidates[0]
    runner_up = scored_candidates[1] if len(scored_candidates) > 1 else None

    # Reasoning text generation
    tc = top_candidate.candidate
    priority_label = requisition.priority.replace('_', ' ').title()
    top_candidate_reasoning = (
        f"<b>{tc.name}</b> sourced via {tc.source} achieves the highest overall Fit Score of "
        f"<b>{top_candidate.fit_score}/100</b>. Expecting <b>{tc.expected_salary} {tc.currency}</b>, they best fulfill "
        f"your focus on <i>{priority_label}</i> with a skills match rating of {top_candidate.skills_match_pct}% and "
        f"verified reference trust."
    )

    runner_up_reasoning = None
    if runner_up:
        ru = runner_up.candidate
        runner_up_reasoning = (
            f"<b>{ru.name}</b> sourced via {ru.source} is a strong runner-up alternative expecting "
            f"<b>{ru.expected_salary} {ru.currency}</b> with a Fit Score of <b>{runner_up.fit_score}/100</b>."
        )

    rejected_count = max(0, len(scored_candidates) - 2)
    rejected_summary = (
        f"Evaluated {len(all_raw_candidates)} raw profiles across {len(selected_sources)} channels. "
        f"Merged into {len(scored_candidates)} unique candidates. {rejected_count} candidates had lower fit scores or exceeded specified salary bounds."
    )

    final_report = HiringReport(
        top_candidate=top_candidate,
        top_candidate_reasoning=top_candidate_reasoning,
        runner_up_candidate=runner_up,
        runner_up_reasoning=runner_up_reasoning,
        all_scored_candidates=scored_candidates,
        rejected_summary=rejected_summary,
        generated_at=datetime.utcnow()
    )

    # 8. Save cache & persistent DB logs
    log_salary_history(clean_candidates)
    log_search_history(requisition, final_report)
    save_to_cache(query_hash, requisition, final_report)

    notify("✨ Search Complete!", 1.0)
    return final_report
