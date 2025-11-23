# simulation.py

from typing import Dict, List, Set
from dataclasses import dataclass
from architecture_model import Architecture, build_dependency_graphs


@dataclass
class FailureResult:
    failed_component: str
    impacted_components: List[str]        # including the failed one
    user_visible_impact: bool
    severity_score: float                 # 0–10
    notes: str = ""                       # optional text


def _get_public_entrypoints(arch: Architecture) -> List[str]:
    """
    Public components (typically user entrypoints like web frontends, API gateways).
    """
    return [
        name
        for name, comp in arch.components.items()
        if comp.public
    ]


def simulate_failure(arch: Architecture, failed_component: str) -> FailureResult:
    """
    Simulate a single component failure.

    Uses reverse dependency graph to find all components that become impacted.
    """
    if failed_component not in arch.components:
        raise ValueError(f"Component '{failed_component}' not found in architecture.")

    forward_graph, reverse_graph = build_dependency_graphs(arch)

    # BFS/DFS on reverse graph to find all components that depend (directly or indirectly) on the failed component
    impacted: Set[str] = set()
    stack: List[str] = [failed_component]

    while stack:
        current = stack.pop()
        if current in impacted:
            continue
        impacted.add(current)

        # Who depends on 'current'?
        for dependent in reverse_graph.get(current, []):
            if dependent not in impacted:
                stack.append(dependent)

    impacted_list = list(impacted)

    # Check if any public entrypoint is impacted
    public_entrypoints = _get_public_entrypoints(arch)
    user_visible_impact = any(name in impacted for name in public_entrypoints)

    severity_score = compute_severity(arch, impacted_list, user_visible_impact)

    notes = (
        "User-facing components are affected."
        if user_visible_impact
        else "No direct impact on public entrypoints."
    )

    return FailureResult(
        failed_component=failed_component,
        impacted_components=sorted(impacted_list),
        user_visible_impact=user_visible_impact,
        severity_score=severity_score,
        notes=notes,
    )


def compute_severity(
    arch: Architecture,
    impacted_components: List[str],
    user_visible_impact: bool,
) -> float:
    """
    Severity scoring (0–10) taking into account:
    - number of impacted components
    - user-visible impact
    - critical component types
    - component criticality (low/medium/high)
    """
    components = arch.components
    score = 0.0

    # 1) Base: number of impacted components
    score += min(len(impacted_components) * 1.0, 5.0)  # cap at 5

    # 2) Extra weight if public components are impacted
    if user_visible_impact:
        score += 3.0

    # 3) Extra weight for certain critical types
    critical_types = {"database", "gateway", "external_api", "queue"}

    for name in impacted_components:
        comp = components[name]
        if comp.ctype in critical_types:
            score += 0.5

        # 4) Criticality weighting
        crit = comp.criticality.lower()
        if crit == "high":
            score += 1.0
        elif crit == "medium":
            score += 0.5
        # low: +0

    # Clamp to 0–10
    if score > 10.0:
        score = 10.0
    if score < 0.0:
        score = 0.0

    return round(score, 2)


def generate_failure_scenarios(arch: Architecture) -> List[str]:
    """
    Select components that are good candidates for failure simulation.
    Priority given to critical types.
    """
    critical_types = {"database", "gateway", "external_api", "queue"}
    scenarios = []

    for name, comp in arch.components.items():
        if comp.ctype in critical_types:
            scenarios.append(name)

    # If none found, fallback to all components
    if not scenarios:
        scenarios = list(arch.components.keys())

    return scenarios
