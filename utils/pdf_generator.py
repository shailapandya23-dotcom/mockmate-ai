from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)


COLOR_PRIMARY = colors.HexColor("#DC3545")
COLOR_DARK = colors.HexColor("#2D3436")
COLOR_GREEN = colors.HexColor("#27AE60")
COLOR_ORANGE = colors.HexColor("#F39C12")
COLOR_LIGHT_BG = colors.HexColor("#FFF5F5")


def _score_color(score):
    if score >= 8:
        return COLOR_GREEN
    elif score >= 6:
        return COLOR_ORANGE
    return COLOR_PRIMARY


def generate_pdf(candidate_name, domain, difficulty, question_count, overall_score, summary, evaluations, questions):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=28,
        textColor=COLOR_PRIMARY,
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=14,
        textColor=COLOR_DARK,
        spaceAfter=20,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=COLOR_PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
        borderPadding=(0, 0, 4, 0),
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=COLOR_DARK,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=14,
    )
    score_style = ParagraphStyle(
        "ScoreStyle",
        parent=styles["Normal"],
        fontSize=48,
        textColor=COLOR_PRIMARY,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=4,
    )
    score_label_style = ParagraphStyle(
        "ScoreLabel",
        parent=styles["Normal"],
        fontSize=12,
        textColor=COLOR_DARK,
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    info_label_style = ParagraphStyle(
        "InfoLabel",
        parent=styles["Normal"],
        fontSize=10,
        textColor=COLOR_DARK,
        fontName="Helvetica-Bold",
        spaceAfter=2,
    )
    info_value_style = ParagraphStyle(
        "InfoValue",
        parent=styles["Normal"],
        fontSize=10,
        textColor=COLOR_DARK,
        spaceAfter=8,
    )
    bullet_style = ParagraphStyle(
        "BulletStyle",
        parent=body_style,
        leftIndent=16,
        bulletIndent=8,
        spaceAfter=4,
    )

    story = []

    story.append(Paragraph("MockMate AI", title_style))
    story.append(Paragraph("Technical Interview Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_PRIMARY))
    story.append(Spacer(1, 16))

    info_data = [
        ["Candidate Name", candidate_name],
        ["Date", datetime.now().strftime("%B %d, %Y")],
        ["Domain", domain],
        ["Difficulty", difficulty],
        ["Total Questions", str(question_count)],
    ]
    info_table = Table(info_data, colWidths=[160, 320])
    info_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (-1, -1), COLOR_DARK),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ]
        )
    )
    story.append(info_table)
    story.append(Spacer(1, 20))

    story.append(HRFlowable(width="60%", thickness=1, color=COLOR_LIGHT_BG))
    story.append(Spacer(1, 8))

    score_val = round(overall_score, 1)
    score_color = _score_color(score_val)
    score_text_color = f"#{score_color.hexval()}"
    story.append(
        Paragraph(
            f'<font color="{score_text_color}">{score_val}</font>',
            score_style,
        )
    )
    story.append(Paragraph("Overall Score / 10", score_label_style))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Skill Breakdown", heading_style))
    skills = summary.get("skill_breakdown", {})
    skill_data = [["Skill", "Score", ""]]
    for label, key in [
        ("Technical Accuracy", "technical_accuracy"),
        ("Clarity", "clarity"),
        ("Depth", "depth"),
        ("Communication", "communication"),
    ]:
        val = skills.get(key, 5)
        bar_color = _score_color(val)
        bar_html = f'<font color="#{bar_color.hexval()}">{"█" * int(val)}{"░" * (10 - int(val))} {val}/10</font>'
        skill_data.append([label, bar_html, ""])

    skill_table = Table(skill_data, colWidths=[160, 350])
    base_style = [
        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), COLOR_DARK),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica"),
    ]
    for i in range(1, len(skill_data)):
        base_style.append(("BACKGROUND", (0, i), (-1, i), COLOR_LIGHT_BG if i % 2 == 0 else colors.white))
    skill_table.setStyle(TableStyle(base_style))
    story.append(skill_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Strengths", heading_style))
    for area in summary.get("strongest_areas", []):
        story.append(Paragraph(f"• {area}", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Areas for Improvement", heading_style))
    for area in summary.get("weakest_areas", []):
        story.append(Paragraph(f"• {area}", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Learning Recommendations", heading_style))
    for topic in summary.get("recommended_topics", []):
        story.append(Paragraph(f"• {topic}", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Personalized Learning Path", heading_style))
    for i, step in enumerate(summary.get("learning_path", []), 1):
        story.append(Paragraph(f"{i}. {step}", bullet_style))
    story.append(Spacer(1, 20))

    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_LIGHT_BG))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Question-wise Evaluation", heading_style))
    story.append(Spacer(1, 8))

    q_data = [["#", "Question", "Score", "Key Feedback"]]
    for i, (q, ev) in enumerate(zip(questions, evaluations), 1):
        q_short = q[:60] + "..." if len(q) > 60 else q
        score = ev.get("overall", 5)
        feedback = ev.get("feedback", "")[:80] + "..." if len(ev.get("feedback", "")) > 80 else ev.get("feedback", "")
        q_data.append([str(i), q_short, f"{score}/10", feedback])

    q_table = Table(q_data, colWidths=[24, 220, 54, 260])
    q_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TEXTCOLOR", (0, 0), (-1, -1), COLOR_DARK),
                ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 0), (2, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FFCDD2")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_LIGHT_BG]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(q_table)
    story.append(Spacer(1, 24))

    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_LIGHT_BG))
    story.append(Spacer(1, 8))
    footer_text = f"Generated by MockMate AI on {datetime.now().strftime('%B %d, %Y at %H:%M')}"
    story.append(Paragraph(footer_text, ParagraphStyle("Footer", parent=body_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))

    doc.build(story)
    buffer.seek(0)
    return buffer
