# ai_summary_agent.py

from typing import Tuple

from orchestrator import SystemReport

# Optional LLM client (Gemini)
try:
    from llm_client import LLMClient
except Exception:
    LLMClient = None  # type: ignore


def _report_to_simple_dict(report: SystemReport) -> dict:
    """
    Lightweight conversion of SystemReport into a JSON-friendly dict
    that we can send to the LLM. We keep only the important fields.
    """
    return {
        "system_name": report.system_name,
        "overall_resilience_score": report.overall_resilience_score,
        "worst_case_severity": report.worst_case_severity,
        "scenarios": [
            {
                "scenario_name": s.scenario_name,
                "failed_component": s.failed_component,
                "severity": s.severity,
                "user_visible_impact": s.user_visible_impact,
                "impacted_components": list(s.impacted_components),
            }
            for s in report.scenarios
        ],
        "security_risks": [
            {
                "component": r.component,
                "risk_type": r.risk_type,
                "severity": r.severity,
                "description": r.description,
                "suggestion": r.suggestion,
            }
            for r in report.security_risks
        ],
    }


def _clean_text(text: str) -> str:
    """
    Remove markdown artifacts like **, ##, *, etc.
    Ensures clean, professional output.
    """
    replacements = [
        ("**", ""),
        ("##", ""),
        ("#", ""),
        ("*", ""),
        ("•", ""),
        ("\u2022", ""),  # bullet char
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    # Strip leading/trailing spaces on each line and drop empty lines
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def generate_ai_summary(report: SystemReport) -> Tuple[str, bool]:
    """
    Generate a high-level AI-style summary.

    Returns:
        (summary_text, used_llm)
        used_llm = True if Gemini was successfully used, else False.
    """

    # Fallback deterministic summary (no LLM)
    fallback_summary = (
        "AI Insight Summary\n"
        "The system was analyzed successfully. Review failure scenarios and remediation "
        "sections to improve resilience and security posture."
    )

    # If LLMClient isn't available at all, immediately fallback
    if LLMClient is None:
        print("[ai_summary_agent] LLMClient not available, using heuristic summary.")
        return fallback_summary, False

    try:
        client = LLMClient()
        report_dict = _report_to_simple_dict(report)

        prompt = f"""
You are an expert Site Reliability Engineer and Security Architect.

You are given the JSON representation of an automated resilience & security analysis
for a software system.

IMPORTANT SCORING INTERPRETATION:
overall_resilience_score is on a 0–10 scale where:
- 0–3   = LOW resilience (system is highly vulnerable)
- 3–7   = MODERATE resilience (system has weaknesses)
- 7–10  = HIGH resilience (system is robust)

You MUST align your language with this scale.
Do NOT describe a system with score below 3 as "moderate" or "strong".

Tasks:
1. Provide a clear overall assessment using the correct resilience category.
2. Highlight the most critical failure scenarios and their real-world impact.
3. Summarize the security posture in practical terms.
4. Recommend 2–4 high-impact improvements.

Writing rules:
- Use clean professional language.
- Do NOT use markdown, bullet symbols, asterisks, or hashes.
- No emojis.
- No casual tone.
- Keep it readable and structured like a professional engineering executive summary.

JSON Input:
{report_dict}
"""


        response = client.model.generate_content(prompt)
        raw_text = (getattr(response, "text", "") or "").strip()

        if not raw_text:
            print("[ai_summary_agent] Empty response from LLM, using heuristic summary.")
            return fallback_summary, False

        clean = _clean_text(raw_text)

        final_output = (
            f"AI Insight Summary\n"
            f"Powered by Gemini ({client.model_name})\n\n"
            f"{clean}"
        )

        return final_output, True

    except Exception as e:
        # If anything goes wrong, log to console and fallback
        print("[ai_summary_agent] LLM call failed, using heuristic summary. Error:", e)
        return fallback_summary, False
