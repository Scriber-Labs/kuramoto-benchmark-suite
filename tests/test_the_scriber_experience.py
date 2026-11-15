# tests/test_the_scriber_experience.py
"""
test_the_scriber_experience.py

Unit and regression tests for The Scriber Experience (TSE) frontend suite:
- Gradient engine (RGB interpolation, hex conversions, multi_gradient output)
- Semantic messaging (ANSI 256-color palettes, icons, banners)
- Baseline CLI user interface
- Mermaid diagram theme engine & builder
- Matplotlib/Seaborn visualization bootstrap
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

# Ensure frontend/ is in sys.path
frontend_dir = Path(__file__).parent.parent / "frontend"
if str(frontend_dir) not in sys.path:
    sys.path.insert(0, str(frontend_dir))

from the_scriber_experience.cli.baseline import BaselineCLI
from the_scriber_experience.cli.gradient import (
    PRESETS,
    hex_to_rgb,
    interpolate_rgb,
    multi_gradient,
    rgb_to_hex,
)
from the_scriber_experience.cli.messaging import (
    EIGENSCRIBE_PALETTE,
    STYLE_MAP,
    ansi_256,
    cli_banner,
    cli_info,
    cli_rule,
    cli_success,
    cli_table,
    supports_256_color,
)
from the_scriber_experience.theme import (
    EIGENSCRIBE_MERMAID_THEME_VARIABLES,
    MermaidDiagram,
    create_boilerplate_diagram,
    create_pipeline_diagram,
    create_sequence_diagram,
    export_all_boilerplates,
    get_mermaid_frontmatter,
)
from the_scriber_experience.visuals import (
    EIGEN_CYAN,
    VIBRANT_10_NODES,
    apply_eigenscribe_style,
    create_styled_figure,
    phase_cmap,
    plot_order_parameter,
    plot_phase_series,
)


def test_gradient_color_math():
    """Verify hex to RGB conversions, bounds, and linear interpolation."""
    assert hex_to_rgb("#00a6ff") == (0, 166, 255)
    assert hex_to_rgb("a855f7") == (168, 85, 247)
    assert rgb_to_hex((0, 166, 255)) == "#00a6ff"

    with pytest.raises(ValueError):
        hex_to_rgb("invalid")

    c1 = (0, 0, 0)
    c2 = (100, 200, 50)
    assert interpolate_rgb(c1, c2, 0.0) == (0, 0, 0)
    assert interpolate_rgb(c1, c2, 1.0) == (100, 200, 50)
    assert interpolate_rgb(c1, c2, 0.5) == (50, 100, 25)


def test_multi_gradient_formatting():
    """Verify multi_gradient string generation and preset handling."""
    text = "KURAMOTO SUITE"
    grad = multi_gradient(text, PRESETS["electric"])
    assert "\033[38;2;" in grad
    assert "\033[0m" in grad

    # Empty text
    assert multi_gradient("") == ""

    # Single character
    single = multi_gradient("A", PRESETS["electric"])
    assert "A" in single

    # Too few stops
    with pytest.raises(ValueError):
        multi_gradient("Test", ["#ffffff"])


import re

def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text for verification."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_messaging_palette_and_helpers(capsys):
    """Verify Eigenscribe palette integrity and semantic messaging."""
    assert "eigen_blue" in EIGENSCRIBE_PALETTE
    assert "eigen_cyan" in EIGENSCRIBE_PALETTE
    assert "eigen_purple" in EIGENSCRIBE_PALETTE
    assert "info" in STYLE_MAP

    cli_banner("TEST APP", "Subtitle", width=40)
    cli_info("Test Info Message")
    cli_success("Test Success Message")
    cli_rule(width=40)
    cli_table([{"Col1": "Val1"}], title="Table Title")

    captured = capsys.readouterr()
    clean_out = strip_ansi(captured.out)
    assert "TEST APP" in clean_out
    assert "Subtitle" in clean_out
    assert "Test Info Message" in clean_out
    assert "Test Success Message" in clean_out


def test_baseline_cli_initialization():
    """Verify BaselineCLI class attributes and execution."""
    cli = BaselineCLI(app_name="Custom CLI", version="2.0.0", width=50)
    assert cli.app_name == "Custom CLI"
    assert cli.version == "2.0.0"
    assert cli.width == 50


def test_mermaid_frontmatter_and_theme():
    """Verify YAML frontmatter generation for Mermaid diagrams."""
    fm = get_mermaid_frontmatter()
    assert "config:" in fm
    assert "theme: base" in fm
    assert 'background: "#0D1117"' in fm
    assert 'primaryColor: "#14B5FF"' in fm
    assert "fontFamily: \"'Aclonica', sans-serif\"" in fm
    assert "---\n" in fm


def test_mermaid_diagram_builder():
    """Verify MermaidDiagram fluent API builder."""
    diag = MermaidDiagram(title="Test Architecture", direction="TD")
    sg = diag.add_subgraph("Layer1", "1️⃣ Client Layer")
    n1 = sg.add_node("CLI", "CLI Suite", shape="rect", style_class="primary")
    n2 = diag.add_node("Core", "Core Engine", shape="round", style_class="success")
    diag.add_link("CLI", "Core", "Dispatches to")

    rendered = diag.render()
    assert "flowchart TD" in rendered
    assert 'subgraph Layer1["1️⃣ Client Layer"]' in rendered
    assert 'CLI["CLI Suite"]:::primary' in rendered
    assert 'Core("Core Engine"):::success' in rendered
    assert 'CLI -->|"Dispatches to"| Core' in rendered
    assert "classDef primary" in rendered


def test_mermaid_template_factories(tmp_path):
    """Verify pre-built template factories and export helpers."""
    bp = create_boilerplate_diagram()
    assert "Client_API" in bp
    assert "Integrator_Ecosystem" in bp

    pipe = create_pipeline_diagram([("S1", "Stage 1"), ("S2", "Stage 2")])
    assert "flowchart LR" in pipe
    assert "S1" in pipe and "S2" in pipe

    seq = create_sequence_diagram(
        participants=[("A", "Client"), ("B", "Server")],
        messages=[("A", "B", "Request data")],
    )
    assert "sequenceDiagram" in seq
    assert "participant A as Client" in seq

    # Export test
    written = export_all_boilerplates(root_dir=tmp_path)
    assert len(written) == 3
    for p in written:
        assert p.exists()
        assert p.stat().st_size > 500


def test_visuals_bootstrap_and_plots():
    """Verify Matplotlib/Seaborn theme bootstrap and plotting helpers."""
    apply_eigenscribe_style()
    assert phase_cmap is not None
    assert len(VIBRANT_10_NODES) == 10

    t = np.linspace(0.0, 1.0, 10)
    theta = np.zeros((10, 4))
    r = np.ones(10) * 0.95

    fig, (ax1, ax2) = create_styled_figure(nrows=1, ncols=2)
    plot_phase_series(t, theta, ax=ax1)
    plot_order_parameter(t, r, ax=ax2)

    assert ax1.get_title() == "Oscillator Phase Evolution"
    assert ax2.get_title() == "Kuramoto Order Parameter r(t)"
    plt.close(fig)
