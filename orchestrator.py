# orchestrator.py

from dataclasses import dataclass
from typing import List, Optional

from architecture_model import Architecture
from simulation import simulate_failure, generate_failure_scenarios
from security_analysis import SecurityRisk, analyze_security
from agent_context import AgentContext


@dataclass
class ScenarioSummary:
    scenario_name: str
    failed_component: str
    severity: float
    user_visible_impact: bool
    impacted_components: List[str]


@dataclass
class SystemReport:
    system_name: str
    scenarios: List[ScenarioSummary]
    security_risks: List[SecurityRisk]
    overall_resilience_score: float  # 0–10, higher is better
    worst_case_severity: float       # max severity across scenarios


# ---------- AGENTS ----------

class FailureSimulationAgent:
    """
    Agent responsible for exploring failure scenarios and summarizing
    their impact on the system.
    """

    def __init__(self, name: str = "failure_simulation_agent"):
        self.name = name

    def run(self, arch: Architecture, context: Optional[AgentContext] = None) -> List[ScenarioSummary]:
        """
        Generate failure scenarios and run simulations on each.
        Returns a list of ScenarioSummary objects.
        """
        if context:
            context.log(self.name, "start", system_name=arch.system_name)

        scenario_ids = generate_failure_scenarios(arch)
        scenario_summaries: List[ScenarioSummary] = []

        for failed_component in scenario_ids:
            result = simulate_failure(arch, failed_component)

            scenario_summaries.append(
                ScenarioSummary(
                    scenario_name=f"{failed_component} FAILURE",
                    failed_component=failed_component,
                    severity=result.severity_score,
                    user_visible_impact=result.user_visible_impact,
                    impacted_components=sorted(result.impacted_components),
                )
            )

        if context:
            context.log(
                self.name,
                "done",
                scenarios=len(scenario_summaries),
                failed_components=scenario_ids,
            )

        return scenario_summaries


class SecurityAnalysisAgent:
    """
    Agent responsible for performing security risk analysis
    on the given architecture.
    """

    def __init__(self, name: str = "security_analysis_agent"):
        self.name = name

    def run(self, arch: Architecture, context: Optional[AgentContext] = None) -> List[SecurityRisk]:
        """
        Run security analysis and return a list of SecurityRisk objects.
        """
        if context:
            context.log(self.name, "start", system_name=arch.system_name)

        risks = analyze_security(arch)

        if context:
            context.log(self.name, "done", risk_count=len(risks))

        return risks


class ReportingAgent:
    """
    Agent responsible for aggregating the outputs of other agents
    into a single SystemReport object.
    """

    def __init__(self, name: str = "reporting_agent"):
        self.name = name

    def run(
        self,
        arch: Architecture,
        scenarios: List[ScenarioSummary],
        security_risks: List[SecurityRisk],
        context: Optional[AgentContext] = None,
    ) -> SystemReport:
        """
        Build a SystemReport from scenario summaries and security risks.
        """
        if context:
            context.log(self.name, "start", scenarios=len(scenarios), risks=len(security_risks))

        if scenarios:
            severities = [s.severity for s in scenarios]
            avg_severity = sum(severities) / len(severities)
            worst_severity = max(severities)
        else:
            avg_severity = 0.0
            worst_severity = 0.0

        # Resilience score: invert average severity
        resilience_score = max(0.0, 10.0 - avg_severity)

        report = SystemReport(
            system_name=arch.system_name,
            scenarios=scenarios,
            security_risks=security_risks,
            overall_resilience_score=round(resilience_score, 2),
            worst_case_severity=round(worst_severity, 2),
        )

        if context:
            context.shared_state["overall_resilience_score"] = report.overall_resilience_score
            context.shared_state["worst_case_severity"] = report.worst_case_severity
            context.log(self.name, "done")

        return report


class OrchestratorAgent:
    """
    High-level coordinator agent.
    It sequences:
    1. Failure simulation
    2. Security analysis
    3. Reporting
    """

    def __init__(
        self,
        failure_agent: FailureSimulationAgent | None = None,
        security_agent: SecurityAnalysisAgent | None = None,
        reporting_agent: ReportingAgent | None = None,
        name: str = "orchestrator_agent",
    ):
        self.name = name
        self.failure_agent = failure_agent or FailureSimulationAgent()
        self.security_agent = security_agent or SecurityAnalysisAgent()
        self.reporting_agent = reporting_agent or ReportingAgent()

    def run(self, arch: Architecture, context: Optional[AgentContext] = None) -> SystemReport:
        """
        Execute the full multi-agent pipeline:
        - simulate failures
        - analyze security
        - aggregate into a system-level report
        """
        if context:
            context.log(self.name, "start", system_name=arch.system_name)

        # 1) Failure simulation agent
        scenarios = self.failure_agent.run(arch, context)

        # 2) Security analysis agent
        security_risks = self.security_agent.run(arch, context)

        # 3) Reporting agent
        report = self.reporting_agent.run(arch, scenarios, security_risks, context)

        if context:
            context.log(self.name, "done")

        return report


# ---------- PUBLIC HELPERS (BACKWARDS COMPATIBLE) ----------

def generate_system_report(arch: Architecture, context: Optional[AgentContext] = None) -> SystemReport:
    """
    Generate a SystemReport for the given architecture.
    Optionally accepts an AgentContext for logging & shared state.
    """
    orchestrator = OrchestratorAgent()
    return orchestrator.run(arch, context)


def print_system_report(report: SystemReport) -> None:
    """
    Nicely prints a system-level resilience & security report.
    """
    print(f"SYSTEM RESILIENCE & SECURITY REPORT for: {report.system_name}")
    print("=" * 60)

    print(f"\nOverall Resilience Score (0–10, higher is better): {report.overall_resilience_score}")
    print(f"Worst-case Scenario Severity (0–10): {report.worst_case_severity}")

    # ---- Failure scenarios ----
    print("\n--- Failure Scenarios ---")
    if not report.scenarios:
        print("No failure scenarios generated.")
    else:
        # Sort by severity descending
        sorted_scenarios = sorted(
            report.scenarios,
            key=lambda s: s.severity,
            reverse=True,
        )
        for i, s in enumerate(sorted_scenarios, start=1):
            print(f"\nScenario {i}: {s.scenario_name}")
            print(f"  Failed Component   : {s.failed_component}")
            print(f"  Severity           : {s.severity}")
            print(f"  User-visible Impact: {s.user_visible_impact}")
            print(f"  Impacted Components: {', '.join(s.impacted_components)}")


    # ---- Security risks ----
    print("\n--- Security Risks ---")
    if not report.security_risks:
        print("✅ No immediate high-level security risks detected.")
    else:
        for i, risk in enumerate(report.security_risks, start=1):
            print(f"\n[{i}] Component : {risk.component}")
            print(f"   Risk Type  : {risk.risk_type}")
            print(f"   Severity   : {risk.severity}")
            print(f"   Explanation: {risk.description}")
            print(f"   Mitigation : {risk.suggestion}")

    print("\nEnd of report.")
