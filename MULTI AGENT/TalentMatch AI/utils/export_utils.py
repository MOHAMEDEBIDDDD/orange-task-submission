import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from models.schemas import HiringReport

def export_to_excel(report: HiringReport) -> bytes:
    """Export hiring report candidates and summary to an Excel file bytes stream."""
    output = io.BytesIO()

    rows = []
    for sc in report.all_scored_candidates:
        c = sc.candidate
        ri = sc.reference_insight
        rows.append({
            "Candidate Name": c.name,
            "Expected Salary": c.expected_salary,
            "Currency": c.currency,
            "Source Channel": c.source,
            "Interview Score": c.interview_score,
            "Endorsements Count": c.endorsements_count,
            "Fit Score (0-100)": sc.fit_score,
            "Skills Match %": sc.skills_match_pct,
            "Within Salary Range": "Yes" if sc.within_salary_range else "No",
            "Verification Status": ri.verification_status if ri else "N/A",
            "Pros": ", ".join(ri.pros) if ri else "",
            "Cons": ", ".join(ri.cons) if ri else "",
            "Profile URL": c.profile_url
        })

    df_candidates = pd.DataFrame(rows)

    # Summary dataframe
    summary_data = {
        "Key": ["Top Candidate", "Top Candidate Salary", "Top Candidate Source", "Runner Up", "Generated Date"],
        "Value": [
            report.top_candidate.candidate.name,
            f"{report.top_candidate.candidate.expected_salary} {report.top_candidate.candidate.currency}",
            report.top_candidate.candidate.source,
            report.runner_up_candidate.candidate.name if report.runner_up_candidate else "N/A",
            report.generated_at.strftime("%Y-%m-%d %H:%M:%S")
        ]
    }
    df_summary = pd.DataFrame(summary_data)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Executive Summary", index=False)
        df_candidates.to_excel(writer, sheet_name="All Candidates", index=False)

    return output.getvalue()

def export_to_pdf(report: HiringReport) -> bytes:
    """Generate a clean executive PDF hiring report using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#4F46E5"),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = styles['BodyText']

    # Header
    story.append(Paragraph("TalentMatch AI — Hiring Recommendation Report", title_style))
    story.append(Paragraph(f"Generated on: {report.generated_at.strftime('%Y-%m-%d %H:%M')}", body_style))
    story.append(Spacer(1, 12))

    # Top Candidate Section
    story.append(Paragraph("🏆 Top Candidate Recommendation", h2_style))
    tc = report.top_candidate.candidate
    tc_text = f"<b>{tc.name}</b><br/>Expected Salary: <b>{tc.expected_salary} {tc.currency}</b> via {tc.source}<br/>Fit Score: <b>{report.top_candidate.fit_score}/100</b>"
    story.append(Paragraph(tc_text, body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Reasoning:</b> {report.top_candidate_reasoning}", body_style))
    story.append(Spacer(1, 12))

    # Runner Up Section
    if report.runner_up_candidate:
        story.append(Paragraph("🥈 Runner-Up Candidate", h2_style))
        ru = report.runner_up_candidate.candidate
        ru_text = f"<b>{ru.name}</b><br/>Expected Salary: <b>{ru.expected_salary} {ru.currency}</b> via {ru.source}<br/>Fit Score: <b>{report.runner_up_candidate.fit_score}/100</b>"
        story.append(Paragraph(ru_text, body_style))
        if report.runner_up_reasoning:
            story.append(Paragraph(f"<b>Reasoning:</b> {report.runner_up_reasoning}", body_style))
        story.append(Spacer(1, 12))

    # Comparison Table
    story.append(Paragraph("📊 Candidate Comparison Summary", h2_style))
    table_data = [["Candidate", "Source", "Expected Salary", "Fit Score", "Verification"]]

    for sc in report.all_scored_candidates[:10]:  # Top 10 candidates
        table_data.append([
            sc.candidate.name[:35] + ("..." if len(sc.candidate.name) > 35 else ""),
            sc.candidate.source,
            f"{sc.candidate.expected_salary} {sc.candidate.currency}",
            f"{sc.fit_score}",
            sc.reference_insight.verification_status if sc.reference_insight else "N/A"
        ])

    t = Table(table_data, colWidths=[200, 75, 85, 55, 65])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t)

    doc.build(story)
    return buffer.getvalue()
