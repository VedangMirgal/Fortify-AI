# architecture_model.py

from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import yaml


@dataclass
class Component:
    name: str
    ctype: str              # e.g. "service", "database", "gateway", "queue", "external_api", "web_client"
    public: bool = False    # exposed to internet / end user
    depends_on: List[str] = field(default_factory=list)
    criticality: str = "medium"  # "low" | "medium" | "high"


@dataclass
class Architecture:
    system_name: str
    components: Dict[str, Component]  # key = component name

    @classmethod
    def from_dict(cls, data: Dict) -> "Architecture":
        """Create Architecture from a Python dict (parsed YAML/JSON)."""
        system_name = data.get("system_name", "Unnamed System")
        components_data = data.get("components", [])

        components: Dict[str, Component] = {}
        for comp in components_data:
            name = comp["name"]
            ctype = comp.get("type", "service")
            public = bool(comp.get("public", False))
            depends_on = comp.get("depends_on", []) or []
            criticality = comp.get("criticality", "medium")

            components[name] = Component(
                name=name,
                ctype=ctype,
                public=public,
                depends_on=depends_on,
                criticality=criticality,
            )

        return cls(system_name=system_name, components=components)


def load_architecture_from_yaml(path: str) -> Architecture:
    """Load architecture from a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Architecture.from_dict(data)


def build_dependency_graphs(arch: Architecture) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Build forward and reverse dependency graphs.

    forward_graph[comp] = list of components it depends on.
    reverse_graph[comp] = list of components that depend on it.
    """
    components = arch.components

    forward_graph: Dict[str, List[str]] = {}
    reverse_graph: Dict[str, List[str]] = {name: [] for name in components.keys()}

    for name, comp in components.items():
        forward_graph[name] = []
        for dep in comp.depends_on:
            forward_graph[name].append(dep)
            if dep not in reverse_graph:
                reverse_graph[dep] = []
            reverse_graph[dep].append(name)

    # Ensure every node appears in both dicts
    for name in components.keys():
        forward_graph.setdefault(name, [])
        reverse_graph.setdefault(name, [])

    return forward_graph, reverse_graph
