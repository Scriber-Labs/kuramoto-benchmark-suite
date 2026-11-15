# frontend/the_scriber_experience/visuals.py
"""
visuals.py

Scientific Visualization & Plotting Bootstrap for Matplotlib, Pyplot, and Seaborn.
Conforms to Eigenscribe / Scriber Labs Design System and glassmorphic color standards.
Provides dark-mode rcParams, cyclic phase colormaps, high-contrast palette cycles,
network topology plotting, and publication-ready figure builders.

Usage
-----
>>> from the_scriber_experience.visuals import apply_eigenscribe_style, create_styled_figure, phase_cmap
>>> apply_eigenscribe_style()
>>> fig, ax = create_styled_figure(figsize=(8, 5))
>>> ax.set_title("Eigenscribe Visualization")

Author: Eigenscribe
Date: October 2026
Last Updated: November 2026
"""

from __future__ import annotations

from typing import Any, Final, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Colormap, LinearSegmentedColormap
from numpy.typing import NDArray

__all__: list[str] = [
    # Surface & Accent Tokens
    "COLOR_BG",
    "COLOR_SURFACE",
    "COLOR_SURFACE_ELEVATED",
    "COLOR_TEXT",
    "COLOR_TEXT_MUTED",
    "COLOR_TEXT_ACCENT",
    "COLOR_BORDER",
    "COLOR_GRID",
    # EIGEN Spectrum & Ramps
    "EIGEN_CYAN",
    "EIGEN_SKY",
    "EIGEN_BLUE",
    "EIGEN_PURPLE",
    "EIGEN_PALETTE_CYCLE",
    "VIBRANT_10_NODES",
    # Colormaps
    "phase_cmap",
    "get_eigenscribe_cmap",
    # Plotting & Styling API
    "apply_eigenscribe_style",
    "create_styled_figure",
    "plot_phase_series",
    "plot_order_parameter",
]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------

# Foundation Surface & Text Tokens
COLOR_BG: Final[str] = "#0d1117"
COLOR_SURFACE: Final[str] = "#161b22"
COLOR_SURFACE_ELEVATED: Final[str] = "#21262d"
COLOR_TEXT: Final[str] = "#f0f6fc"
COLOR_TEXT_MUTED: Final[str] = "#8b949e"
COLOR_TEXT_ACCENT: Final[str] = "#c8f8ff"
COLOR_BORDER: Final[str] = "#30363d"
COLOR_GRID: Final[str] = "#21262d"

# Canonical EIGEN Spectrum
EIGEN_CYAN: Final[str] = "#00e8ff"
EIGEN_SKY: Final[str] = "#14b5ff"
EIGEN_BLUE: Final[str] = "#3a98ff"
EIGEN_PURPLE: Final[str] = "#7952f5"

# 4-Color Primary Palette Cycle
EIGEN_PALETTE_CYCLE: Final[list[str]] = [
    "#14b5ff",  # Cyan / Bright Sky
    "#9b7dff",  # Lavender / Purple
    "#22f792",  # Neon Green
    "#f78166",  # Coral / Amber
    "#ff40a1",  # Hot Pink
    "#00e8ff",  # Pure Electric Cyan
]

# Vibrant 10-Node Spectrum
VIBRANT_10_NODES: Final[list[str]] = [
    "#fff9d6",  # Node 0 (Light Pale Yellow)
    "#00ffff",  # Node 1 (Electric Cyan)
    "#00e8ff",  # Node 2 (Bright Ice Cyan)
    "#14b5ff",  # Node 3 (Deep Sky Blue)
    "#0070eb",  # Node 4 (Royal Blue)
    "#ffd94a",  # Node 5 (Bright Warm Amber)
    "#7952f5",  # Node 6 (Medium Slate Violet)
    "#5e17eb",  # Node 7 (Deep Indigo)
    "#ff66b3",  # Node 8 (Hot Pink Accent)
    "#00c853",  # Node 9 (Vibrant Emerald)
]

# Cyclic colormap for S^1 phase angles [-pi, pi]
_CYC_STOPS = [
    (0.00, "#14b5ff"),  # Cyan
    (0.25, "#7952f5"),  # Purple
    (0.50, "#ff40a1"),  # Magenta
    (0.75, "#ff783d"),  # Coral Orange
    (1.00, "#14b5ff"),  # Back to Cyan
]
phase_cmap: Final[LinearSegmentedColormap] = LinearSegmentedColormap.from_list(
    "eigenscribe_cyclic_phase", _CYC_STOPS, N=256
)


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API / Matplotlib & Pyplot Bootstrap
# -----------------------------------------------------------------------------------------------------------


def get_eigenscribe_cmap(name: str = "phase") -> Colormap:
    """
    Retrieve an Eigenscribe colormap instance.

    Parameters
    ----------
    name : str, default='phase'
        Colormap name ('phase', 'electric', 'sunset').

    Returns
    -------
    Colormap
        Matplotlib colormap object.
    """
    if name == "sunset":
        return LinearSegmentedColormap.from_list(
            "eigenscribe_sunset", ["#ff6b35", "#f7c548", "#ff40a1"], N=256
        )
    return phase_cmap


def apply_eigenscribe_style(dark: bool = True) -> None:
    """
    Apply Eigenscribe theme styling to global Matplotlib rcParams.

    Parameters
    ----------
    dark : bool, default=True
        Whether to enforce high-contrast dark mode.
    """
    if not dark:
        plt.style.use("default")
        return

    rc_overrides = {
        "figure.facecolor": COLOR_BG,
        "figure.edgecolor": COLOR_BG,
        "axes.facecolor": COLOR_SURFACE,
        "axes.edgecolor": COLOR_BORDER,
        "axes.labelcolor": COLOR_TEXT,
        "axes.titlecolor": COLOR_TEXT,
        "axes.grid": True,
        "axes.grid.which": "major",
        "grid.color": COLOR_GRID,
        "grid.linestyle": "--",
        "grid.linewidth": 0.6,
        "grid.alpha": 0.7,
        "xtick.color": COLOR_TEXT_MUTED,
        "ytick.color": COLOR_TEXT_MUTED,
        "xtick.labelcolor": COLOR_TEXT,
        "ytick.labelcolor": COLOR_TEXT,
        "text.color": COLOR_TEXT,
        "legend.facecolor": COLOR_SURFACE_ELEVATED,
        "legend.edgecolor": COLOR_BORDER,
        "legend.labelcolor": COLOR_TEXT,
        "axes.prop_cycle": mpl.cycler(color=EIGEN_PALETTE_CYCLE),
        "lines.linewidth": 1.75,
        "lines.solid_capstyle": "round",
    }
    plt.rcParams.update(rc_overrides)


def create_styled_figure(
    nrows: int = 1,
    ncols: int = 1,
    *,
    figsize: tuple[float, float] = (10.0, 5.5),
    sharex: bool = False,
    sharey: bool = False,
    **kwargs: Any,
) -> tuple[plt.Figure, Any]:
    """
    Create a Matplotlib figure and subplots styled with Eigenscribe dark mode defaults.

    Parameters
    ----------
    nrows : int, default=1
        Number of subplot rows.
    ncols : int, default=1
        Number of subplot columns.
    figsize : tuple[float, float], default=(10.0, 5.5)
        Figure size in inches.
    sharex : bool, default=False
        Share x-axis across subplots.
    sharey : bool, default=False
        Share y-axis across subplots.

    Returns
    -------
    tuple[plt.Figure, Any]
        Configured (figure, axes) tuple.
    """
    apply_eigenscribe_style(dark=True)
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=figsize,
        sharex=sharex,
        sharey=sharey,
        **kwargs,
    )
    return fig, axes


def plot_phase_series(
    time: NDArray[np.floating],
    theta: NDArray[np.floating],
    *,
    title: str = "Oscillator Phase Evolution",
    ax: plt.Axes | None = None,
    wrap: bool = True,
) -> plt.Axes:
    """
    Plot multi-oscillator phase trajectory time series.

    Parameters
    ----------
    time : NDArray
        Time coordinate array.
    theta : NDArray
        Phase angle matrix of shape (timesteps, n_oscillators).
    title : str, default='Oscillator Phase Evolution'
        Subplot title.
    ax : plt.Axes, optional
        Target Matplotlib axes.
    wrap : bool, default=True
        Whether to wrap phases into [-pi, pi].

    Returns
    -------
    plt.Axes
        The updated Matplotlib axes object.
    """
    if ax is None:
        _, ax = create_styled_figure()

    phases = (theta + np.pi) % (2 * np.pi) - np.pi if wrap else theta
    n_oscillators = phases.shape[1]

    for i in range(n_oscillators):
        color = VIBRANT_10_NODES[i % len(VIBRANT_10_NODES)]
        ax.plot(time, phases[:, i], color=color, alpha=0.85, label=f"θ_{i}")

    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Time (s)", fontsize=11)
    ax.set_ylabel("Phase Angle (rad)", fontsize=11)
    if wrap:
        ax.set_ylim(-np.pi * 1.05, np.pi * 1.05)

    return ax


def plot_order_parameter(
    time: NDArray[np.floating],
    r: NDArray[np.floating],
    *,
    title: str = "Kuramoto Order Parameter r(t)",
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """
    Plot Kuramoto synchronization order parameter r(t) in [0, 1].

    Parameters
    ----------
    time : NDArray
        Time coordinate array.
    r : NDArray
        Order parameter magnitude array of shape (timesteps,).
    title : str, default='Kuramoto Order Parameter r(t)'
        Subplot title.
    ax : plt.Axes, optional
        Target Matplotlib axes.

    Returns
    -------
    plt.Axes
        The updated Matplotlib axes object.
    """
    if ax is None:
        _, ax = create_styled_figure()

    ax.plot(time, r, color=EIGEN_CYAN, linewidth=2.2, label="Order Parameter r(t)")
    ax.axhline(1.0, color=COLOR_TEXT_MUTED, linestyle=":", alpha=0.5)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Time (s)", fontsize=11)
    ax.set_ylabel("Synchronization Strength r", fontsize=11)
    ax.set_ylim(-0.02, 1.05)

    return ax


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Validate colormaps, style application, and figure generation."""
    print("💨 Running visuals.py smoke test...")
    apply_eigenscribe_style()
    assert phase_cmap is not None
    assert len(VIBRANT_10_NODES) == 10

    t = np.linspace(0, 1, 20)
    theta = np.zeros((20, 4))
    r = np.ones(20) * 0.95

    fig, ax = create_styled_figure()
    plot_phase_series(t, theta, ax=ax)
    plot_order_parameter(t, r, ax=ax)
    plt.close(fig)

    print("✅ visuals.py smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Demonstrate visual styling."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
