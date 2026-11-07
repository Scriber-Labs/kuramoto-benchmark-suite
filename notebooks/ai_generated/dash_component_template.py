# examples/ai_generated_notebooks/dash_component_template.py
"""
Dash component template for the Kuramoto Benchmark Suite.

Provides two visualizations for the `kuramoto-dash-app` project:
  - Phase portrait on S¹: oscillators as points on a unit circle, colored by phase.
  - Adjacency matrix heatmap: color-coded network structure view.

Supports both JSON (from ``kuramoto dash-export``) and JSONL (from ``--stream``)
export formats.

Author: Eigenscribe & Junie
Date: 10-2026
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import hsv_to_rgb
from numpy.typing import NDArray

# Use non-interactive backend for standalone execution
matplotlib.use("Agg")

# ------------------------------------------------------------------------------
# 0️⃣ Definitions, Constants & Types
# ------------------------------------------------------------------------------

# Dark theme colors from kuramoto.analysis.viz
THEME_BG: str = "#0d1117"
CARD_BG: str = "#161b22"
TEXT_PRIMARY: str = "#c9d1d9"
TEXT_MUTED: str = "#8b949e"

# ------------------------------------------------------------------------------
# 1️⃣ Public API — Data Loaders
# ------------------------------------------------------------------------------


def load_json_export(path: str) -> Dict[str, Any]:
    """
    Load an enriched JSON export from ``kuramoto dash-export``.

    Parameters
    ----------
    path : str
        Path to the JSON file produced by ``kuramoto dash-export``.

    Returns
    -------
    Dict[str, Any]
        Dictionary with ``metadata`` and ``data`` keys. The ``data`` field
        contains ``time``, ``theta`` (shape T×N), ``R``, ``psi``, and
        ``locking`` arrays.
    """
    with open(path, "r") as f:
        raw = json.load(f)

    metadata = raw["metadata"]
    split_data = raw["data"]

    # Reconstruct from pandas split format
    columns = split_data["columns"]
    index = split_data["index"]
    data_rows = split_data["data"]

    n_oscillators = metadata["n_oscillators"]

    # Extract time and node columns
    time = np.array(index, dtype=np.float64)
    node_cols = [c for c in columns if c.startswith("node_")]
    theta = np.array([row[columns.index(c)] for row in data_rows for c in node_cols])
    theta = theta.reshape(len(index), -1)

    R = np.array([row[columns.index("order_parameter")] for row in data_rows])
    psi = np.array([row[columns.index("mean_field_phase")] for row in data_rows])
    locking = np.array([row[columns.index("locking_fraction")] for row in data_rows])

    return {
        "metadata": metadata,
        "time": time,
        "theta": theta,
        "R": R,
        "psi": psi,
        "locking": locking,
    }


def load_jsonl_export(path: str) -> Dict[str, Any]:
    """
    Load a streaming JSONL export from ``kuramoto dash-export --stream``.

    Parameters
    ----------
    path : str
        Path to the JSONL file produced by ``kuramoto dash-export --stream``.

    Returns
    -------
    Dict[str, Any]
        Dictionary with ``metadata`` and ``data`` keys, same structure as
        ``load_json_export()``.
    """
    with open(path, "r") as f:
        lines = f.readlines()

    # Parse header line (comment, starts with '# ')
    header_line = lines[0].strip()
    if header_line.startswith("# "):
        metadata = json.loads(header_line[2:])["metadata"]
    else:
        metadata = {}

    # Parse data lines
    times: List[float] = []
    thetas: List[List[float]] = []
    rs: List[float] = []
    psis: List[float] = []
    lockings: List[float] = []

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        times.append(obj["t"])
        thetas.append(obj["theta"])
        rs.append(obj["R"])
        psis.append(obj["psi"])
        lockings.append(obj["locking"])

    return {
        "metadata": metadata,
        "time": np.array(times),
        "theta": np.array(thetas),
        "R": np.array(rs),
        "psi": np.array(psis),
        "locking": np.array(lockings),
    }


def load_export(path: str) -> Dict[str, Any]:
    """
    Auto-detect and load either JSON or JSONL export format.

    Parameters
    ----------
    path : str
        Path to the export file (.json or .jsonl).

    Returns
    -------
    Dict[str, Any]
        Loaded dataset with metadata and time series data.
    """
    path_obj = Path(path)
    if path_obj.suffix == ".jsonl":
        return load_jsonl_export(str(path_obj))
    else:
        return load_json_export(str(path_obj))

# ------------------------------------------------------------------------------
# 2️⃣ Visualization Functions
# ------------------------------------------------------------------------------


def plot_phase_portrait(
    theta: NDArray[np.floating],
    timestep_idx: int,
    ax: plt.Axes | None = None,
    show_plot: bool = False,
) -> plt.Figure:
    """
    Plot oscillators as points on the S¹ unit circle, colored by phase.

    Each oscillator is represented as a point on the unit circle at angle
    θᵢ. The color encodes the phase angle using an HSV colormap where
    hue = θ/2π.

    Parameters
    ----------
    theta : NDArray[np.floating]
        Phase array of shape (T, N) or (N,) for a single timestep.
    timestep_idx : int
        Index of the timestep to plot (if theta is 2D).
    ax : matplotlib.axes.Axes, optional
        Existing axes to plot on. If None, a new figure is created.
    show_plot : bool, default False
        Whether to call plt.show() after plotting.

    Returns
    -------
    plt.Figure
        The figure containing the phase portrait.
    """
    if theta.ndim == 2:
        phases = theta[timestep_idx]
    else:
        phases = theta

    n = len(phases)

    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(6, 6), facecolor=THEME_BG)
    else:
        fig = ax.figure

    # Compute x, y coordinates on unit circle
    x = np.cos(phases)
    y = np.sin(phases)

    # Color by phase: hue = θ / 2π
    hues = phases / (2 * np.pi)
    # Shift hue so 0 is at the top (12 o'clock)
    hues = (hues + 0.25) % 1.0
    colors = hsv_to_rgb(np.column_stack([hues, np.ones(n), np.ones(n)]))

    # Plot unit circle
    circle = plt.Circle((0, 0), 1, color=TEXT_MUTED, fill=False, linewidth=0.5, alpha=0.3)
    ax.add_patch(circle)

    # Plot oscillators
    scatter = ax.scatter(x, y, c=colors, s=100, edgecolors=THEME_BG, linewidths=1.5, zorder=5)

    # Draw lines from origin to each point
    for xi, yi in zip(x, y):
        ax.plot([0, xi], [0, yi], color=TEXT_MUTED, linewidth=0.3, alpha=0.2)

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    ax.set_facecolor(CARD_BG)
    ax.set_title(f"Phase Portrait on S¹ (timestep {timestep_idx})", color=TEXT_PRIMARY, fontsize=14)
    ax.set_xlabel("cos(θ)", color=TEXT_MUTED)
    ax.set_ylabel("sin(θ)", color=TEXT_MUTED)
    ax.tick_params(colors=TEXT_MUTED)

    # Add colorbar legend
    sm = plt.cm.ScalarMappable(
        cmap=plt.cm.hsv,
        norm=plt.Normalize(vmin=0, vmax=2 * np.pi),
    )
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation="vertical", pad=0.02)
    cbar.set_label("Phase θ (rad)", color=TEXT_PRIMARY)
    cbar.ax.tick_params(colors=TEXT_MUTED)

    fig.tight_layout()
    if show_plot:
        plt.show()

    return fig


def plot_adjacency_heatmap(
    adjacency: NDArray[np.floating],
    ax: plt.Axes | None = None,
    show_plot: bool = False,
) -> plt.Figure:
    """
    Plot a color-coded heatmap of the adjacency matrix.

    The adjacency matrix shows which oscillators are connected. Oscillator
    indices match the phase portrait, so the two visualizations can be
    viewed together.

    Parameters
    ----------
    adjacency : NDArray[np.floating]
        Adjacency matrix of shape (N, N).
    ax : matplotlib.axes.Axes, optional
        Existing axes to plot on. If None, a new figure is created.
    show_plot : bool, default False
        Whether to call plt.show() after plotting.

    Returns
    -------
    plt.Figure
        The figure containing the adjacency heatmap.
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(6, 5), facecolor=THEME_BG)
    else:
        fig = ax.figure

    n = adjacency.shape[0]

    # Use seaborn heatmap with dark theme
    sns.heatmap(
        adjacency,
        ax=ax,
        cmap="viridis",
        cbar_kws={"label": "Connection weight"},
        linewidths=0.5,
        linecolor=THEME_BG,
    )

    ax.set_facecolor(CARD_BG)
    ax.set_title("Adjacency Matrix Heatmap", color=TEXT_PRIMARY, fontsize=14)
    ax.set_xlabel("Oscillator index", color=TEXT_MUTED)
    ax.set_ylabel("Oscillator index", color=TEXT_MUTED)
    ax.tick_params(colors=TEXT_MUTED)

    # Style colorbar
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(colors=TEXT_MUTED)
    cbar.set_label("Connection weight", color=TEXT_PRIMARY)

    fig.tight_layout()
    if show_plot:
        plt.show()

    return fig


def create_combined_view(
    data: Dict[str, Any],
    timestep_idx: int = 0,
    output_path: str | None = None,
) -> Tuple[plt.Figure, plt.Figure]:
    """
    Create both phase portrait and adjacency heatmap side by side.

    Parameters
    ----------
    data : Dict[str, Any]
        Loaded dataset from ``load_export()``.
    timestep_idx : int, default 0
        Timestep index for the phase portrait.
    output_path : str, optional
        If provided, save the combined figure to this path.

    Returns
    -------
    Tuple[plt.Figure, plt.Figure]
        Tuple of (phase_portrait_fig, adjacency_heatmap_fig).
    """
    theta = data["theta"]
    metadata = data["metadata"]

    # Get adjacency matrix from metadata if available
    topology_stats = metadata.get("topology_stats", {})
    n = metadata.get("n_oscillators", theta.shape[1])

    # Reconstruct adjacency from topology type
    topology_type = metadata.get("topology_type", "complete")
    if topology_type == "complete":
        adjacency = np.ones((n, n))
        np.fill_diagonal(adjacency, 0)
    else:
        # Default to complete if topology info is not in metadata
        adjacency = np.ones((n, n))
        np.fill_diagonal(adjacency, 0)

    fig_phase = plot_phase_portrait(theta, timestep_idx)
    fig_adj = plot_adjacency_heatmap(adjacency)

    if output_path:
        fig_phase.savefig(output_path, dpi=150, facecolor=THEME_BG, bbox_inches="tight")

    return fig_phase, fig_adj

# ------------------------------------------------------------------------------
# 💨 Smoke Test
# ------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Sanity check: generate sample data and create plots."""
    print("💨 Running dash_component_template smoke test...")

    # Generate sample data
    rng = np.random.default_rng(42)
    n = 10
    timesteps = 50
    theta = rng.uniform(0, 2 * np.pi, (timesteps, n))
    # Add some phase evolution
    for t in range(1, timesteps):
        theta[t] = theta[t - 1] + rng.normal(0.1, 0.05, n)

    # Create sample metadata
    metadata = {
        "n_oscillators": n,
        "timesteps": timesteps,
        "coupling": 1.5,
        "topology_type": "complete",
        "topology_stats": {"num_nodes": n, "num_edges": n * (n - 1) // 2},
    }

    data = {
        "metadata": metadata,
        "time": np.linspace(0, 1, timesteps),
        "theta": theta,
        "R": np.random.rand(timesteps),
        "psi": np.random.rand(timesteps) * 2 * np.pi,
        "locking": np.zeros(timesteps),
    }

    # Test phase portrait
    fig_phase = plot_phase_portrait(theta, timestep_idx=0)
    print(" ... ✔️ Phase portrait created.")

    # Test adjacency heatmap
    adjacency = np.ones((n, n))
    np.fill_diagonal(adjacency, 0)
    fig_adj = plot_adjacency_heatmap(adjacency)
    print(" ... ✔️ Adjacency heatmap created.")

    # Test combined view
    fig_phase2, fig_adj2 = create_combined_view(data, timestep_idx=10)
    print(" ... ✔️ Combined view created.")

    # Test JSONL loader with sample data
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False, mode="w") as f:
        # Write header
        f.write(f'# {json.dumps({"metadata": metadata})}\n')
        # Write data lines
        for t_idx in range(timesteps):
            line = json.dumps({
                "t": float(data["time"][t_idx]),
                "theta": theta[t_idx].tolist(),
                "R": float(data["R"][t_idx]),
                "psi": float(data["psi"][t_idx]),
                "locking": float(data["locking"][t_idx]),
            })
            f.write(line + "\n")
        tmp_path = f.name

    try:
        loaded = load_jsonl_export(tmp_path)
        assert loaded["metadata"]["n_oscillators"] == n
        assert loaded["theta"].shape == (timesteps, n)
        print(" ... ✔️ JSONL loader works correctly.")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    plt.close("all")
    print("\n✅ All dash_component_template smoke tests passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
