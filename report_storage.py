# report_storage.py

import json
from dataclasses import asdict
from typing import List, Dict, Any
from orchestrator import SystemReport, ScenarioSummary
from security_analysis import SecurityRisk


def system_report_to_dict(report: SystemReport) -> Dict[str, Any]:
    """
    Convert SystemReport (with nested dataclasses) to a plain dict
    that can be saved as JSON.
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
                "impacted_components": s.impacted_components,
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


def save_report(report: SystemReport, path: str) -> None:
    data = system_report_to_dict(report)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"\n[info] Report saved to {path}")


def load_report(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
