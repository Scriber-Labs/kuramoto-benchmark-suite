# frontend/the_scriber_experience/theme.py
"""
theme.py

Eigenscribe Theme Generator & Builder Engine for Mermaid.js Diagrams.
Provides structured configuration frontmatter, custom CSS injection, dark-mode
cosmic color palettes, node styling classes, and fluent diagram builders
for publication-ready Markdown/Mermaid architecture diagrams.

Conforms to The Scriber Experience (TSE) 4-layer taxonomy and gold standard design rules.

Usage
-----
>>> from the_scriber_experience.theme import (
...     get_mermaid_frontmatter,
...     create_boilerplate_diagram,
...     MermaidDiagram,
... )
>>> frontmatter = get_mermaid_frontmatter(direction="TD")
>>> boilerplate = create_boilerplate_diagram()
>>> diagram = MermaidDiagram(title="My Architecture", direction="TD")
>>> diagram.add_node("API", "REST & CLI API", layer="primary")
>>> print(diagram.render())

Author: Eigenscribe
Date: October 2026
Last Updated: November 2026
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final, Sequence

__all__: list[str] = [
    # Constants & Palette
    "EIGENSCRIBE_MERMAID_THEME_VARIABLES",
    "EIGENSCRIBE_MERMAID_THEME_CSS",
    "EIGENSCRIBE_MERMAID_CLASS_DEFS",
    # Frontmatter & Directive Generators
    "get_mermaid_frontmatter",
    "get_mermaid_init_directive",
    "format_mermaid_header",
    # Diagram Builders & Helpers
    "MermaidNode",
    "MermaidLink",
    "MermaidSubgraph",
    "MermaidDiagram",
    # Template Factories
    "create_boilerplate_diagram",
    "create_pipeline_diagram",
    "create_sequence_diagram",
    "save_mermaid_diagram",
    "export_all_boilerplates",
]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------

# Canonical theme variables matching Eigenscribe Glassmorphism & High-Contrast Standards
EIGENSCRIBE_MERMAID_THEME_VARIABLES: Final[dict[str, Any]] = {
    "background": "#0D1117",
    "primaryColor": "#14B5FF",
    "primaryTextColor": "#F0F6FC",
    "primaryBorderColor": "#14B5FF",
    "lineColor": "#14B5FF",
    "secondaryColor": "#0070EB",
    "tertiaryColor": "#0D1117",
    "fontFamily": "'Aclonica', sans-serif",
    "fontSize": "15px",
    "clusterBkg": "rgba(255, 255, 255, 0.03)",
    "clusterBorder": "#30363D",
    "edgeLabelBackground": "#0D1117",
    "nodeSpacing": 45,
    "rankSpacing": 75,
    "borderRadius": "10",
}

# Theme CSS injection for Katex, MathJax, node glows, and rounded clusters
EIGENSCRIBE_MERMAID_THEME_CSS: Final[str] = (
    ".node rect, .node circle, .node ellipse, .node polygon, .node path { "
    "fill-opacity: 0.9; stroke-width: 2px; }\n"
    "    .cluster rect { rx: 16; ry: 16; }\n"
    "    .nodeLabel, .edgeLabel, .cluster-label, .cluster-label text, .label, .label text, "
    "text, .katex, .katex *, .MathJax, .MathJax *, mjx-container, mjx-container * { "
    "color: #F0F6FC !important; fill: #F0F6FC !important; -webkit-text-fill-color: #F0F6FC !important; }"
)

# Semantic class definitions for node styling
EIGENSCRIBE_MERMAID_CLASS_DEFS: Final[dict[str, str]] = {
    "primary": "fill:#002b4d,stroke:#14b5ff,stroke-width:2px,color:#f0f6fc",
    "secondary": "fill:#1f1347,stroke:#7952f5,stroke-width:2px,color:#f0f6fc",
    "success": "fill:#003820,stroke:#22f792,stroke-width:2px,color:#f0f6fc",
    "warning": "fill:#3d2400,stroke:#f78166,stroke-width:2px,color:#f0f6fc",
    "accent": "fill:#38002a,stroke:#ff40a1,stroke-width:2px,color:#f0f6fc",
    "cosmic": "fill:#0a0f1f,stroke:#c8f8ff,stroke-width:2px,color:#f0f6fc",
    "subtle": "fill:#161b22,stroke:#30363d,stroke-width:1.5px,color:#8b949e",
}


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API / Frontmatter & Directive Generators
# -----------------------------------------------------------------------------------------------------------


def get_mermaid_frontmatter(
    direction: str = "TD",
    curve: str = "basis",
    custom_vars: dict[str, Any] | None = None,
    custom_css: str | None = None,
) -> str:
    """
    Generate the canonical YAML frontmatter configuration block for Mermaid diagrams.

    Parameters
    ----------
    direction : str, default='TD'
        Flowchart direction ('TD', 'LR', 'BT', 'RL').
    curve : str, default='basis'
        Connection line curve interpolation ('basis', 'linear', 'cardinal', 'step').
    custom_vars : dict[str, Any], optional
        Optional theme variable overrides.
    custom_css : str, optional
        Optional additional CSS rules to append.

    Returns
    -------
    str
        Full YAML frontmatter header string including opening and closing `---`.
    """
    theme_vars = dict(EIGENSCRIBE_MERMAID_THEME_VARIABLES)
    if custom_vars:
        theme_vars.update(custom_vars)

    css_body = EIGENSCRIBE_MERMAID_THEME_CSS
    if custom_css:
        css_body = f"{css_body}\n    {custom_css}"

    var_lines = []
    for k, v in theme_vars.items():
        if isinstance(v, str):
            var_lines.append(f'    {k}: "{v}"')
        else:
            var_lines.append(f"    {k}: {v}")

    var_block = "\n".join(var_lines)

    return (
        "---\n"
        "config:\n"
        "  theme: base\n"
        "  look: classic\n"
        "  themeVariables:\n"
        f"{var_block}\n"
        "  flowchart:\n"
        f"    curve: {curve}\n"
        "    useMaxWidth: true\n"
        "    htmlLabels: true\n"
        "  themeCSS: |\n"
        f"    {css_body}\n"
        "---\n"
    )


def get_mermaid_init_directive(custom_vars: dict[str, Any] | None = None) -> str:
    """
    Generate inline Mermaid `%%{init: ...}%%` directive string.

    Parameters
    ----------
    custom_vars : dict[str, Any], optional
        Optional theme variable overrides.

    Returns
    -------
    str
        Mermaid init directive string.
    """
    theme_vars = dict(EIGENSCRIBE_MERMAID_THEME_VARIABLES)
    if custom_vars:
        theme_vars.update(custom_vars)

    parts = []
    for k, v in theme_vars.items():
        if isinstance(v, str):
            parts.append(f"'{k}': '{v}'")
        else:
            parts.append(f"'{k}': {v}")

    inner_dict = ", ".join(parts)
    return f"%%{{init: {{'theme': 'base', 'themeVariables': {{{inner_dict}}}}} }}%%"


def format_mermaid_header(diagram_type: str = "flowchart TD") -> str:
    """
    Return frontmatter followed by diagram type definition.

    Parameters
    ----------
    diagram_type : str, default='flowchart TD'
        Mermaid diagram type header.

    Returns
    -------
    str
        Complete header ready for node and subgraph definitions.
    """
    return f"{get_mermaid_frontmatter()}{diagram_type}\n"


# -----------------------------------------------------------------------------------------------------------
# 2️⃣ Diagram Components & Fluent Builder
# -----------------------------------------------------------------------------------------------------------


class MermaidNode:
    """
    Representation of a single Mermaid diagram node.

    Parameters
    ----------
    node_id : str
        Unique identifier for the node.
    label : str
        Display text or HTML/LaTeX formatted label.
    shape : str, default='rect'
        Node boundary shape ('rect', 'round', 'stadium', 'circle', 'diamond', 'cylinder').
    style_class : str, optional
        Semantic class name ('primary', 'secondary', 'success', 'warning', 'accent', 'cosmic').
    """

    def __init__(
        self,
        node_id: str,
        label: str,
        shape: str = "rect",
        style_class: str | None = None,
    ) -> None:
        self.node_id = node_id
        self.label = label
        self.shape = shape
        self.style_class = style_class

    def render(self) -> str:
        """Render the node definition in Mermaid flowchart syntax."""
        label_escaped = self.label.replace('"', "&quot;")
        if self.shape == "round":
            s = f'{self.node_id}("{label_escaped}")'
        elif self.shape == "stadium":
            s = f'{self.node_id}(["{label_escaped}"])'
        elif self.shape == "circle":
            s = f'{self.node_id}(("{label_escaped}"))'
        elif self.shape == "diamond":
            s = f'{self.node_id}{{"{label_escaped}"}}'
        elif self.shape == "cylinder":
            s = f'{self.node_id}[("{label_escaped}")]'
        else:  # rect
            s = f'{self.node_id}["{label_escaped}"]'

        if self.style_class:
            s += f":::{self.style_class}"
        return s


class MermaidLink:
    """
    Representation of a directional or bidirectional connection between nodes.

    Parameters
    ----------
    source_id : str
        Source node identifier.
    target_id : str
        Target node identifier.
    label : str, optional
        Link label text.
    link_type : str, default='arrow'
        Connection line type ('arrow', 'dotted', 'thick', 'bidirectional', 'open').
    """

    def __init__(
        self,
        source_id: str,
        target_id: str,
        label: str | None = None,
        link_type: str = "arrow",
    ) -> None:
        self.source_id = source_id
        self.target_id = target_id
        self.label = label
        self.link_type = link_type

    def render(self) -> str:
        """Render the link definition in Mermaid syntax."""
        if self.link_type == "dotted":
            connector = "-.->"
            if self.label:
                connector = f"-. {self.label} .->"
        elif self.link_type == "thick":
            connector = "==>"
            if self.label:
                connector = f"== {self.label} ==>"
        elif self.link_type == "bidirectional":
            connector = "<-->"
            if self.label:
                connector = f"<-- {self.label} -->"
        elif self.link_type == "open":
            connector = "---"
            if self.label:
                connector = f"-- {self.label} ---"
        else:  # standard arrow
            if self.label:
                connector = f'-->|"{self.label}"|'
            else:
                connector = "-->"

        return f"{self.source_id} {connector} {self.target_id}"


class MermaidSubgraph:
    """
    Representation of a grouped subgraph or layer.

    Parameters
    ----------
    subgraph_id : str
        Unique subgraph identifier.
    title : str
        Layer title / label.
    """

    def __init__(self, subgraph_id: str, title: str) -> None:
        self.subgraph_id = subgraph_id
        self.title = title
        self.nodes: list[MermaidNode] = []

    def add_node(
        self,
        node_id: str,
        label: str,
        shape: str = "rect",
        style_class: str | None = None,
    ) -> MermaidNode:
        """Add a node into this subgraph."""
        node = MermaidNode(node_id, label, shape=shape, style_class=style_class)
        self.nodes.append(node)
        return node

    def render(self, indent: str = "    ") -> str:
        """Render the subgraph and its member nodes."""
        lines = [f'subgraph {self.subgraph_id}["{self.title}"]']
        for n in self.nodes:
            lines.append(f"{indent}{n.render()}")
        lines.append("end")
        return "\n".join(lines)


class MermaidDiagram:
    """
    Fluent builder for publication-ready Eigenscribe Mermaid diagrams.

    Parameters
    ----------
    title : str, optional
        Diagram title.
    direction : str, default='TD'
        Flowchart direction ('TD', 'LR', 'BT', 'RL').
    curve : str, default='basis'
        Connection curve style ('basis', 'linear', 'cardinal', 'step').
    """

    def __init__(
        self,
        title: str | None = None,
        direction: str = "TD",
        curve: str = "basis",
    ) -> None:
        self.title = title
        self.direction = direction
        self.curve = curve
        self.subgraphs: list[MermaidSubgraph] = []
        self.standalone_nodes: list[MermaidNode] = []
        self.links: list[MermaidLink] = []
        self.class_defs: dict[str, str] = dict(EIGENSCRIBE_MERMAID_CLASS_DEFS)

    def add_subgraph(self, subgraph_id: str, title: str) -> MermaidSubgraph:
        """Create and register a new subgraph layer."""
        sg = MermaidSubgraph(subgraph_id, title)
        self.subgraphs.append(sg)
        return sg

    def add_node(
        self,
        node_id: str,
        label: str,
        shape: str = "rect",
        style_class: str | None = None,
    ) -> MermaidNode:
        """Add a standalone node outside any subgraph."""
        node = MermaidNode(node_id, label, shape=shape, style_class=style_class)
        self.standalone_nodes.append(node)
        return node

    def add_link(
        self,
        source_id: str,
        target_id: str,
        label: str | None = None,
        link_type: str = "arrow",
    ) -> MermaidLink:
        """Add a connection between two nodes."""
        link = MermaidLink(source_id, target_id, label=label, link_type=link_type)
        self.links.append(link)
        return link

    def render(self) -> str:
        """Render the complete Mermaid diagram string with YAML frontmatter."""
        frontmatter = get_mermaid_frontmatter(
            direction=self.direction, curve=self.curve
        )
        body_lines = [f"flowchart {self.direction}\n"]

        if self.title:
            body_lines.append(f"%% Title: {self.title}\n")

        # Subgraphs
        for sg in self.subgraphs:
            body_lines.append(sg.render())
            body_lines.append("")

        # Standalone nodes
        for node in self.standalone_nodes:
            body_lines.append(node.render())

        if self.standalone_nodes:
            body_lines.append("")

        # Links
        for link in self.links:
            body_lines.append(link.render())

        body_lines.append("")

        # Class Definitions
        for cname, cstyle in self.class_defs.items():
            body_lines.append(f"classDef {cname} {cstyle};")

        return frontmatter + "\n".join(body_lines) + "\n"

    def save(self, filepath: str | Path) -> None:
        """Save the rendered diagram to disk."""
        save_mermaid_diagram(self.render(), filepath)


# -----------------------------------------------------------------------------------------------------------
# 3️⃣ Pre-Built Diagram Template Factories
# -----------------------------------------------------------------------------------------------------------


def create_boilerplate_diagram() -> str:
    """
    Generate the gold-standard Eigenscribe multi-layer architecture boilerplate diagram.

    Returns
    -------
    str
        Complete, valid Mermaid diagram source string.
    """
    diag = MermaidDiagram(title="Eigenscribe Architectural Blueprint", direction="TD")

    # Layer 1: Client & High-Level API Layer
    l1 = diag.add_subgraph("Client_API", "1️⃣ Client & High-Level API Layer")
    l1.add_node(
        "CLI",
        "CLI Command Suite<br/>(generate, time, network, psd, qasm)",
        shape="rect",
        style_class="primary",
    )
    l1.add_node(
        "API_Gen",
        "generate_kuramoto_dataset()<br/>Unified Functional API",
        shape="rect",
        style_class="primary",
    )
    l1.add_node(
        "Notebooks",
        "Interactive Research Notebooks<br/>(failure_modes, sanity_checks)",
        shape="rect",
        style_class="cosmic",
    )

    # Layer 2: Model Orchestration & Configuration Layer
    l2 = diag.add_subgraph(
        "Model_Orchestration", "2️⃣ Model Orchestration & Configuration Layer"
    )
    l2.add_node(
        "Config",
        "SimulationConfig & Solver Types<br/>(N, K, topology, dt, seed)",
        shape="rect",
        style_class="secondary",
    )
    l2.add_node(
        "Topology",
        "Network Topologies (load_topology)<br/>Ring, Erdos-Renyi, Small-World, Tree-of-Life",
        shape="rect",
        style_class="secondary",
    )
    l2.add_node(
        "Temporal_Ctrl",
        "Temporal Resolution Controller<br/>Nyquist Guard & Adaptive Step Selection",
        shape="rect",
        style_class="secondary",
    )

    # Layer 3: Dynamical Physics & Algebra Generators
    l3 = diag.add_subgraph("Physics_Law", "3️⃣ Dynamical Physics & Algebra Generators")
    l3.add_node(
        "Phase_Physics",
        "Phase-Space Vector Field (&Ropf;<sup>N</sup>)<br/>d&theta;<sub>i</sub>/dt = &omega;<sub>i</sub> + (K/N) &sum; A<sub>ij</sub> sin(&theta;<sub>j</sub> - &theta;<sub>i</sub>)",
        shape="rect",
        style_class="accent",
    )
    l3.add_node(
        "GA_Physics",
        "2D/3D Clifford Bivector Torque (Cl<sub>2,0</sub> / Cl<sub>3,0</sub>)<br/>&Omega;<sub>i</sub> = &omega;<sub>i</sub> e<sub>12</sub> - K (v<sub>mean,i</sub> &and; v<sub>i</sub>)",
        shape="rect",
        style_class="accent",
    )
    l3.add_node(
        "Quantum_Physics",
        "Quantum SCF Collective Hamiltonian<br/>H(t) = -1/2 &sum;<sub>j</sub> &Omega;<sub>j</sub>(t) &sigma;<sub>j</sub><sup>z</sup>",
        shape="rect",
        style_class="accent",
    )

    # Layer 4: Multi-Manifold Numerical Solvers
    l4 = diag.add_subgraph(
        "Integrator_Ecosystem", "4️⃣ Multi-Manifold Numerical Solvers"
    )
    l4.add_node(
        "RK45_Int",
        "Classical Adaptive RK45<br/>SciPy Dormand-Prince 5(4)",
        shape="rect",
        style_class="success",
    )
    l4.add_node(
        "GA_Rotors",
        "Geometric Algebra Rotor Integrators<br/>Midpoint, Embedded, Lie-RKMK4, Adaptive DOPRI 5(4)",
        shape="rect",
        style_class="success",
    )
    l4.add_node(
        "Quantum_SCF",
        "Quantum SCF Solvers<br/>Statevector, Expectation, Shot Sampling & QASM",
        shape="rect",
        style_class="success",
    )
    l4.add_node(
        "Coprime_Sampler",
        "Dual-Channel Coprime Sub-Nyquist Sampler<br/>M/N Strides & CRT Reconstruction",
        shape="rect",
        style_class="success",
    )

    # Layer 5: Diagnostics, Symmetries & Data Serialization
    l5 = diag.add_subgraph(
        "Diagnostics_Layer", "5️⃣ Diagnostics, Symmetries & Data Serialization"
    )
    l5.add_node(
        "Obs_OP",
        "Order Parameter Engine<br/>r(t) = &lang;exp(i&theta;)&rang; & Synchronization Bounds",
        shape="rect",
        style_class="warning",
    )
    l5.add_node(
        "Obs_Lie",
        "Lie Symmetry & Invariants Tracker<br/>U(1) Invariance, Energy Drift & Symplectic Check",
        shape="rect",
        style_class="warning",
    )
    l5.add_node(
        "Dataset_Out",
        "KuramotoDataset Output<br/>Serialization (.npz, .h5, JSON Telemetry)",
        shape="cylinder",
        style_class="warning",
    )

    # Connect layers
    diag.add_link("CLI", "Config")
    diag.add_link("API_Gen", "Config")
    diag.add_link("Notebooks", "Config")
    diag.add_link("Config", "Topology")
    diag.add_link("Topology", "Phase_Physics")
    diag.add_link("Temporal_Ctrl", "Integrator_Ecosystem")
    diag.add_link("Phase_Physics", "RK45_Int")
    diag.add_link("GA_Physics", "GA_Rotors")
    diag.add_link("Quantum_Physics", "Quantum_SCF")
    diag.add_link("Integrator_Ecosystem", "Obs_OP")
    diag.add_link("Integrator_Ecosystem", "Coprime_Sampler")
    diag.add_link("Obs_OP", "Obs_Lie")
    diag.add_link("Obs_Lie", "Dataset_Out")

    return diag.render()


def create_pipeline_diagram(stages: Sequence[tuple[str, str]]) -> str:
    """
    Generate a linear or multi-stage pipeline diagram.

    Parameters
    ----------
    stages : Sequence[tuple[str, str]]
        List of (stage_id, stage_label) tuples.

    Returns
    -------
    str
        Rendered pipeline diagram.
    """
    diag = MermaidDiagram(title="Pipeline Flow", direction="LR")
    prev_id: str | None = None
    for i, (sid, slabel) in enumerate(stages):
        style = (
            "primary"
            if i == 0
            else ("success" if i == len(stages) - 1 else "secondary")
        )
        diag.add_node(sid, slabel, shape="round", style_class=style)
        if prev_id:
            diag.add_link(prev_id, sid)
        prev_id = sid
    return diag.render()


def create_sequence_diagram(
    participants: Sequence[tuple[str, str]],
    messages: Sequence[tuple[str, str, str]],
) -> str:
    """
    Generate a themed Mermaid sequence diagram.

    Parameters
    ----------
    participants : Sequence[tuple[str, str]]
        List of (alias, label) tuples.
    messages : Sequence[tuple[str, str, str]]
        List of (source, target, message) tuples.

    Returns
    -------
    str
        Rendered sequence diagram.
    """
    lines = [get_mermaid_frontmatter(), "sequenceDiagram\n"]
    for alias, label in participants:
        lines.append(f"    participant {alias} as {label}")
    lines.append("")
    for src, tgt, msg in messages:
        lines.append(f"    {src}->>+{tgt}: {msg}")
    return "\n".join(lines) + "\n"


def save_mermaid_diagram(diagram_str: str, filepath: str | Path) -> None:
    """
    Save a rendered Mermaid diagram string to a file, ensuring parent directories exist.

    Parameters
    ----------
    diagram_str : str
        Rendered diagram text.
    filepath : str or Path
        Target destination file path.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(diagram_str)


def export_all_boilerplates(root_dir: str | Path | None = None) -> list[Path]:
    """
    Export boilerplate Mermaid diagrams into canonical boilerplate directories across the repository.

    Parameters
    ----------
    root_dir : str or Path, optional
        Project root directory. Defaults to current working directory.

    Returns
    -------
    list[Path]
        List of paths where boilerplate diagram files were written.
    """
    base = Path(root_dir or Path.cwd())
    boilerplate_content = create_boilerplate_diagram()

    target_paths = [
        base / "boilerplates" / "mermaid" / "boilerplate_diagram.mmd",
        base / ".scriber-core" / "boilerplates" / "mermaid" / "boilerplate_diagram.mmd",
        base
        / "frontend"
        / "the_scriber_experience"
        / "boilerplates"
        / "boilerplate_diagram.mmd",
    ]

    written: list[Path] = []
    for p in target_paths:
        save_mermaid_diagram(boilerplate_content, p)
        written.append(p)

    return written


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Validate theme variable generation, diagram builder, and boilerplate export."""
    print("💨 Running theme.py smoke test...")

    # Frontmatter validation
    fm = get_mermaid_frontmatter()
    assert "themeVariables:" in fm
    assert 'background: "#0D1117"' in fm
    assert 'primaryColor: "#14B5FF"' in fm
    assert "fontFamily: \"'Aclonica', sans-serif\"" in fm

    # Builder validation
    diag = MermaidDiagram(title="Test Diagram")
    sg = diag.add_subgraph("Layer1", "1️⃣ Layer 1")
    sg.add_node("N1", "Node 1", style_class="primary")
    diag.add_node("N2", "Node 2", style_class="success")
    diag.add_link("N1", "N2", "Step 1")
    rendered = diag.render()
    assert "flowchart TD" in rendered
    assert 'N1["Node 1"]:::primary' in rendered
    assert 'N1 -->|"Step 1"| N2' in rendered

    # Boilerplate factory validation
    bp = create_boilerplate_diagram()
    assert "Client_API" in bp
    assert "Integrator_Ecosystem" in bp
    assert "Diagnostics_Layer" in bp

    # Export validation
    written = export_all_boilerplates()
    assert len(written) == 3
    for p in written:
        assert p.exists()

    print("✅ theme.py smoke test passed. Boilerplate diagrams exported.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Generate and export the Eigenscribe boilerplate Mermaid diagram."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
