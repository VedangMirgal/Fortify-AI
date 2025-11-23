# report_generator.py

from typing import List, Optional
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
)
from reportlab.lib.units import cm

from orchestrator import SystemReport


# ---------- TEXT / MARKDOWN-LIKE REPORT ----------

def generate_text_report(report: SystemReport) -> str:
    """
    Generate a detailed plain-text / markdown-style report.
    This can be saved as .md or .txt.
    """
    lines: List[str] = []

    # Title
    lines.append(f"# System Resilience & Security Report: {report.system_name}\n")

    # Table of Contents
    lines.append("## Table of Contents")
    lines.append("1. Overview")
    lines.append("2. Failure Scenarios")
    lines.append("3. Security Risks")
    lines.append("4. Conclusion\n")

    # 1. Overview
    lines.append("## 1. Overview")
    lines.append(
        f"- **Overall resilience score**: {report.overall_resilience_score} / 10 (higher is better)"
    )
    lines.append(
        f"- **Worst-case scenario severity**: {report.worst_case_severity} / 10"
    )
    lines.append(
        f"- **Number of failure scenarios simulated**: {len(report.scenarios)}"
    )
    lines.append(
        f"- **Number of security risks detected**: {len(report.security_risks)}\n"
    )

    # 2. Failure Scenarios
    lines.append("## 2. Failure Scenarios")
    if not report.scenarios:
        lines.append("No failure scenarios were generated.\n")
    else:
        sorted_scenarios = sorted(
            report.scenarios, key=lambda s: s.severity, reverse=True
        )
        for i, s in enumerate(sorted_scenarios, start=1):
            lines.append(f"### 2.{i} Scenario: {s.scenario_name}")
            lines.append(f"- Failed component: **{s.failed_component}**")
            lines.append(f"- Severity: **{s.severity} / 10**")
            lines.append(f"- User-visible impact: **{s.user_visible_impact}**")
            lines.append(
                f"- Impacted components: {', '.join(s.impacted_components)}\n"
            )

    # 3. Security Risks
    lines.append("## 3. Security Risks")
    if not report.security_risks:
        lines.append("No immediate high-level security risks detected.\n")
    else:
        for i, risk in enumerate(report.security_risks, start=1):
            lines.append(f"### 3.{i} Risk on {risk.component}")
            lines.append(f"- Risk type: **{risk.risk_type}**")
            lines.append(f"- Severity: **{risk.severity}**")
            lines.append(f"- Details: {risk.description}")
            lines.append(f"- Suggested mitigation: {risk.suggestion}\n")

    # 4. Conclusion
    lines.append("## 4. Conclusion")
    lines.append(
        "This report provides a first-pass automated resilience and security assessment "
        "based on the supplied architecture. It is not a replacement for expert review, "
        "but can help teams quickly identify critical weak points and prioritize fixes.\n"
    )

    return "\n".join(lines)


def save_text_report(report: SystemReport, path: str) -> None:
    """
    Save the markdown-style report to a file.
    """
    text = generate_text_report(report)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[info] Text report saved to {path}")


# ---------- PDF REPORT USING REPORTLAB ----------

def _add_page_number(canvas, doc):
    """
    Callback to add page numbers at the bottom of each page.
    """
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(20 * cm, 1 * cm, text)


def generate_pdf_report(
    report: SystemReport,
    path: str,
    graph_image_path: Optional[str] = None,
) -> None:
    """
    Generate a multi-page PDF report with sections, optional architecture graph,
    and page numbers.
    """
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(
        Paragraph(
            f"System Resilience & Security Report: {report.system_name}",
            styles["Title"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    # Table of Contents (static, but structured)
    story.append(Paragraph("Table of Contents", styles["Heading2"]))
    story.append(Paragraph("1. Overview", styles["Normal"]))
    story.append(Paragraph("2. Failure Scenarios", styles["Normal"]))
    story.append(Paragraph("3. Security Risks", styles["Normal"]))
    story.append(Paragraph("4. Conclusion", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # Optional: Architecture graph image
    if graph_image_path is not None and os.path.exists(graph_image_path):
        story.append(Paragraph("Architecture Graph", styles["Heading2"]))
        story.append(
            Image(graph_image_path, width=15 * cm, height=8 * cm)
        )
        story.append(Spacer(1, 0.5 * cm))

    # 1. Overview
    story.append(Paragraph("1. Overview", styles["Heading2"]))
    story.append(
        Paragraph(
            f"Overall resilience score: {report.overall_resilience_score} / 10 (higher is better).",
            styles["Normal"],
        )
    )
    story.append(
        Paragraph(
            f"Worst-case scenario severity: {report.worst_case_severity} / 10.",
            styles["Normal"],
        )
    )
    story.append(
        Paragraph(
            f"Number of failure scenarios simulated: {len(report.scenarios)}.",
            styles["Normal"],
        )
    )
    story.append(
        Paragraph(
            f"Number of security risks detected: {len(report.security_risks)}.",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    # 2. Failure Scenarios
    story.append(Paragraph("2. Failure Scenarios", styles["Heading2"]))
    if not report.scenarios:
        story.append(
            Paragraph(
                "No failure scenarios were generated.",
                styles["Normal"],
            )
        )
    else:
        sorted_scenarios = sorted(
            report.scenarios, key=lambda s: s.severity, reverse=True
        )
        for i, s in enumerate(sorted_scenarios, start=1):
            story.append(
                Paragraph(
                    f"2.{i} Scenario: {s.scenario_name}",
                    styles["Heading3"],
                )
            )
            story.append(
                Paragraph(
                    f"Failed component: {s.failed_component}",
                    styles["Normal"],
                )
            )
            story.append(
                Paragraph(
                    f"Severity: {s.severity} / 10",
                    styles["Normal"],
                )
            )
            story.append(
                Paragraph(
                    f"User-visible impact: {s.user_visible_impact}",
                    styles["Normal"],
                )
            )
            story.append(
                Paragraph(
                    f"Impacted components: {', '.join(s.impacted_components)}",
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 0.3 * cm))

    story.append(PageBreak())

    # 3. Security Risks
    story.append(Paragraph("3. Security Risks", styles["Heading2"]))
    if not report.security_risks:
        story.append(
            Paragraph(
                "No immediate high-level security risks detected.",
                styles["Normal"],
            )
        )
    else:
        for i, risk in enumerate(report.security_risks, start=1):
            story.append(
                Paragraph(
                    f"3.{i} Risk on {risk.component}",
                    styles["Heading3"],
                )
            )
            story.append(
                Paragraph(f"Risk type: {risk.risk_type}", styles["Normal"])
            )
            story.append(
                Paragraph(f"Severity: {risk.severity}", styles["Normal"])
            )
            story.append(
                Paragraph(f"Details: {risk.description}", styles["Normal"])
            )
            story.append(
                Paragraph(
                    f"Suggested mitigation: {risk.suggestion}",
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 0.3 * cm))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("4. Conclusion", styles["Heading2"]))
    story.append(
        Paragraph(
            "This automated report highlights system resilience and security issues "
            "based on the provided architecture. It is intended as a first-pass analysis "
            "to support engineers and architects in improving system robustness.",
            styles["Normal"],
        )
    )

    # Build PDF with page numbers
    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    print(f"[info] PDF report saved to {path}")
