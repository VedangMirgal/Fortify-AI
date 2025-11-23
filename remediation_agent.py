# remediation_agent.py

from dataclasses import dataclass, asdict
from typing import List, Optional

from architecture_model import Architecture
from orchestrator import SystemReport, ScenarioSummary
from security_analysis import SecurityRisk
from agent_context import AgentContext

# Optional LLM client (Gemini). If not available, we just skip AI augmentation.
try:
    from llm_client import LLMClient
except Exception:
    LLMClient = None  # type: ignore


@dataclass
class RemediationSuggestion:
    category: str          # "resilience" | "security" | "architecture"
    target: str            # component name or "system"
    priority: str          # "high" | "medium" | "low"
    title: str             # short heading
    details: str           # longer explanation


def _report_to_simple_dict(report: SystemReport) -> dict:
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


class RemediationAgent:
    """
    Agent that inspects the SystemReport (and architecture)
    and proposes structured remediation suggestions.

    It is primarily rule-based, but can optionally be augmented
    with AI-generated suggestions via Gemini (LLMClient).
    """

    def __init__(self, name: str = "remediation_agent"):
        self.name = name

    def run(
        self,
        arch: Architecture,
        report: SystemReport,
        context: Optional[AgentContext] = None,
    ) -> List[RemediationSuggestion]:
        suggestions: List[RemediationSuggestion] = []

        if context:
            context.log(
                self.name,
                "start",
                system_name=arch.system_name,
                overall_resilience=report.overall_resilience_score,
            )

        # --- 1) Global/system-level resilience suggestions (rule-based) ---
        if report.overall_resilience_score <= 4.0:
            suggestions.append(
                RemediationSuggestion(
                    category="resilience",
                    target="system",
                    priority="high",
                    title="Improve overall fault tolerance",
                    details=(
                        "The overall resilience score is low. Introduce redundancy (replicated services, "
                        "database failover), implement graceful degradation paths, and validate recovery "
                        "procedures for critical components."
                    ),
                )
            )

        # --- 2) Scenario-based, high-severity failures (rule-based) ---
        for scenario in report.scenarios:
            if scenario.severity < 8.0:
                continue

            comp_name = scenario.failed_component
            comp = arch.components.get(comp_name)
            if not comp:
                continue

            if comp.ctype == "database":
                suggestions.append(
                    RemediationSuggestion(
                        category="resilience",
                        target=comp_name,
                        priority="high",
                        title=f"Add replication and backup for {comp_name}",
                        details=(
                            f"When {comp_name} fails, it impacts {len(scenario.impacted_components)} components "
                            f"and is user-visible. Configure primary/replica setups, automated failover, and "
                            f"regular backup/restore drills."
                        ),
                    )
                )
            elif comp.ctype == "gateway":
                suggestions.append(
                    RemediationSuggestion(
                        category="resilience",
                        target=comp_name,
                        priority="high",
                        title=f"Eliminate single point of failure at {comp_name}",
                        details=(
                            f"{comp_name} is a critical gateway whose failure disrupts user access. "
                            "Add multiple gateway instances behind a load balancer and implement health checks."
                        ),
                    )
                )
            elif comp.ctype == "external_api":
                suggestions.append(
                    RemediationSuggestion(
                        category="resilience",
                        target=comp_name,
                        priority="high",
                        title=f"Introduce circuit breakers and fallbacks for {comp_name}",
                        details=(
                            f"{comp_name} is an external dependency whose failure causes a high-severity impact. "
                            "Use circuit breakers, timeouts, retries with backoff, and possibly alternative providers."
                        ),
                    )
                )
            else:
                suggestions.append(
                    RemediationSuggestion(
                        category="resilience",
                        target=comp_name,
                        priority="medium",
                        title=f"Harden {comp_name} against failures",
                        details=(
                            f"{comp_name} shows a high-severity failure scenario. Consider adding redundancy, "
                            "better monitoring, and fallback logic specific to this component."
                        ),
                    )
                )

        # --- 3) Security-risk-driven suggestions (rule-based) ---
        for risk in report.security_risks:
            priority = "high" if risk.severity.lower() == "high" else "medium"
            suggestions.append(
                RemediationSuggestion(
                    category="security",
                    target=risk.component,
                    priority=priority,
                    title=f"Mitigate {risk.risk_type} on {risk.component}",
                    details=risk.suggestion,
                )
            )

        # --- 4) Optional AI-augmented suggestions using Gemini ---
        if LLMClient is not None:
            try:
                client = LLMClient()
                report_dict = _report_to_simple_dict(report)

                base_suggestions = [
                    {
                        "category": s.category,
                        "target": s.target,
                        "priority": s.priority,
                        "title": s.title,
                        "details": s.details,
                    }
                    for s in suggestions
                ]

                extra = client.generate_remediation_suggestions(
                    report_dict, base_suggestions
                )

                for s in extra:
                    suggestions.append(
                        RemediationSuggestion(
                            category=s.get("category", "resilience"),
                            target=s.get("target", "system"),
                            priority=s.get("priority", "medium"),
                            title=s.get("title", "AI-suggested remediation"),
                            details=s.get("details", ""),
                        )
                    )

                if context:
                    context.log(
                        self.name,
                        "llm_enhanced",
                        added_count=len(extra),
                        model=client.model_name,
                    )

            except Exception as e:
                if context:
                    context.log(
                        self.name,
                        "llm_failed",
                        error=str(e),
                    )

        # --- 5) Final bookkeeping ---
        if context:
            context.shared_state["remediation_suggestion_count"] = len(suggestions)
            context.log(self.name, "done", suggestions=len(suggestions))

        return suggestions


def suggestions_to_dict_list(
    suggestions: List[RemediationSuggestion],
) -> List[dict]:
    return [asdict(s) for s in suggestions]
