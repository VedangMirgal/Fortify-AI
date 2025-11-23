# graph_utils.py

from graphviz import Digraph
from architecture_model import Architecture, build_dependency_graphs


def generate_architecture_graph_image(arch: Architecture, output_basename: str) -> str:
    """
    Generate a PNG image of the architecture dependency graph.

    output_basename: path without extension, e.g. "runs/2025.../architecture_graph"
    Returns the final PNG path, e.g. "runs/2025.../architecture_graph.png"
    """
    forward_graph, _ = build_dependency_graphs(arch)

    dot = Digraph(name=arch.system_name, format="png")
    dot.attr(rankdir="LR")  # left-to-right layout

    # Nodes
    for name, comp in arch.components.items():
        shape = "box"
        if comp.ctype == "database":
            shape = "cylinder"
        elif comp.ctype == "queue":
            shape = "diamond"
        elif comp.ctype == "gateway":
            shape = "octagon"

        dot.node(name, label=f"{name}\n({comp.ctype})", shape=shape)

    # Edges (dependencies)
    for src, deps in forward_graph.items():
        for dst in deps:
            dot.edge(src, dst)

    # This will create output_basename + ".png"
    png_path = dot.render(output_basename, cleanup=True)
    return png_path
