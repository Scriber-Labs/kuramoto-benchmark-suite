"""
viz.py

Visualization tools for Kuramoto oscillator networks, phase distributions,
order parameter dynamics, and spectral diagnostics.
Implements unified dark slate theme with glassmorphic accents,
high-contrast perceptually smooth colormaps, standardized typography,
and semantic variable palettes adhering to The Scriber Experience design system.

Author: Eigenscribe
Review status: Reviewed and maintained.
"""

from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Sequence, Tuple

import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.font_manager import findSystemFonts
from matplotlib.text import Text
from numpy.typing import NDArray

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ Definitions, Constants & Design Tokens (The Scriber Experience)
# -----------------------------------------------------------------------------------------------------------

# Look for bundled Aclonica font if available
for _candidate_dir in [
    Path(__file__).resolve().parent.parent / "assets" / "fonts",
    Path(__file__).resolve().parent.parent.parent / "assets" / "fonts",
    Path(__file__).resolve().parent / "assets" / "fonts",
]:
    _cand_font = _candidate_dir / "Aclonica-Regular.ttf"
    if _cand_font.exists():
        try:
            fm.fontManager.addfont(str(_cand_font))
        except Exception:
            pass
        break

# Core Design Tokens
THEME_BG: Final[str] = "#0d1117"  # Dark slate background
CARD_BG: Final[str] = "#161b22"  # Glassmorphic card / panel background
BORDER_COLOR: Final[str] = "#30363d"  # Structural borders and spines
GRID_COLOR: Final[str] = "#21262d"  # Subtle grid lines
TEXT_PRIMARY: Final[str] = "#e6edf3"  # High-contrast primary text
TEXT_MUTED: Final[str] = "#8b949e"  # Muted labels, secondary notes, and ticks

# Core Brand Palette
PROJECT_COLORS: Final[Dict[str, str]] = {
    # Core brand palette
    "cyan_light": "#00FFEE",
    "cyan_blue": "#00E8FF",
    "blue_light": "#14B5FF",
    "blue_mid": "#0A95EB",
    "blue_deep": "#0070EB",
    "indigo": "#5280FF",
    "indigo_blue": "#5280FF",
    "purple_deep": "#A855F7",
    "purple_light": "#7952F5",
    "purple_dark": "#7C5CFF",
    "purple_lavender": "#D8B4FE",
    "pink_vibrant": "#FF66B3",
    "pink_pink": "#F72585",
    "pink_dark": "#AD1457",
    "pink_light": "#FFB4F6",
    "pink_alt": "#FF40A1",
    "orange_warm": "#FF9D57",
    "orange_soft": "#F78166",
    "green_neon": "#31FF48",
    "green_lime": "#70E000",
    "green_light": "#57FFBC",
    "green_emerald": "#059669",
    "green_dark": "#035100",
    "green_jade": "#00FF7F",
    "cyan_green": "#00F5D4",
    "yellow_orange": "#FFD166",
}

# Backwards-compatible palette mapping
SCRIBER_PALETTE: Final[Dict[str, str]] = {
    "bg_deep": THEME_BG,
    "bg_panel": CARD_BG,
    "accent_cyan": PROJECT_COLORS["blue_light"],
    "accent_teal": PROJECT_COLORS["cyan_blue"],
    "accent_purple": PROJECT_COLORS["purple_light"],
    "accent_indigo": PROJECT_COLORS["indigo"],
    "text_primary": TEXT_PRIMARY,
    "text_muted": TEXT_MUTED,
    "grid": GRID_COLOR,
}

# Quantity-Specific Comparison Palette
COMPARISON_PALETTE: Final[Dict[str, Dict[str, str]]] = {
    "potential": {
        "true": "#F72585",  # Vibrant Neon Magenta/Pink (Ground Truth)
        "learned": "#31FF48",  # Luminous Vibrant Green (Learned PINN)
    },
    "wavefunctions": {
        "true": "#F72585",  # Vibrant Eigenscribe Neon Magenta/Pink (Ground Truth)
        "learned": "#31FF48",  # Luminous Vibrant Green (Learned PINN)
    },
    "energy": {
        "true": "#0070EB",  # Deep Royal Blue (Ground Truth)
        "learned": "#00E8FF",  # Light Vivid Sky / Cyan Blue (Learned PINN)
    },
    "density": {
        "true": "#F72585",  # Vibrant Neon Magenta/Pink (Ground Truth)
        "observed": "#7C5CFF",  # Electric Purple (Observed data alias)
        "learned": "#31FF48",  # Luminous Vibrant Green (Learned PINN)
    },
    "order_parameter": {
        "ground_truth": "#00FFEE",  # Bright Electric Cyan
        "euler": "#7952F5",  # Electric Purple
        "rotor": "#00E8FF",  # Cyan Blue
    },
}

COLOR_POTENTIAL_TRUE: Final[str] = COMPARISON_PALETTE["potential"]["true"]
COLOR_POTENTIAL_LEARNED: Final[str] = COMPARISON_PALETTE["potential"]["learned"]
COLOR_WAVEFUNCTION_TRUE: Final[str] = COMPARISON_PALETTE["wavefunctions"]["true"]
COLOR_WAVEFUNCTION_LEARNED: Final[str] = COMPARISON_PALETTE["wavefunctions"]["learned"]
COLOR_ENERGY_TRUE: Final[str] = COMPARISON_PALETTE["energy"]["true"]
COLOR_ENERGY_LEARNED: Final[str] = COMPARISON_PALETTE["energy"]["learned"]
COLOR_DENSITY_TRUE: Final[str] = COMPARISON_PALETTE["density"]["true"]
COLOR_DENSITY_OBSERVED: Final[str] = COMPARISON_PALETTE["density"]["observed"]
COLOR_DENSITY_LEARNED: Final[str] = COMPARISON_PALETTE["density"]["learned"]

COLOR_TRUE: Final[str] = "#F72585"
COLOR_LEARNED: Final[str] = "#31FF48"
COLOR_OBSERVED: Final[str] = "#7C5CFF"
COLOR_POD_MODE: Final[str] = "#0A95EB"
COLOR_POD_ALT: Final[str] = "#FFD166"

LOSS_COLORS: Final[Dict[str, str]] = {
    "Total": PROJECT_COLORS["purple_deep"],
    "Physics": PROJECT_COLORS["blue_light"],
    "Data-fit": PROJECT_COLORS["pink_vibrant"],
    "Smoothness": PROJECT_COLORS["green_jade"],
    "Ordered": PROJECT_COLORS["orange_warm"],
}

FIGURE_2: Final[Dict[str, str]] = {
    "Ground_Truth_Potential": COLOR_POTENTIAL_TRUE,
    "Learned_Potential": COLOR_POTENTIAL_LEARNED,
}

# Golden Ratio Constants
GOLDEN_RATIO: Final[float] = (1.0 + 5.0**0.5) / 2.0  # φ ≈ 1.6180339887
PHI: Final[float] = GOLDEN_RATIO
INV_PHI: Final[float] = 1.0 / GOLDEN_RATIO  # φ⁻¹ ≈ 0.6180339887
INV_PHI2: Final[float] = INV_PHI**2  # φ⁻² ≈ 0.3819660113
INV_PHI3: Final[float] = INV_PHI**3  # φ⁻³ ≈ 0.2360679775
INV_PHI4: Final[float] = INV_PHI**4  # φ⁻⁴ ≈ 0.1458980338

# Semantic Colormaps
temporal_pod_cmap = LinearSegmentedColormap.from_list(
    "temporal_pod_gradient",
    [
        (0.00, "#032B14"),
        (0.25, "#059669"),
        (0.50, "#00FF7F"),
        (0.75, "#31FF48"),
        (1.00, "#CCFFBD"),
    ],
)

spatial_pod_cmap = LinearSegmentedColormap.from_list(
    "spatial_pod_gradient",
    [
        (0.00, "#3B022D"),
        (0.25, "#7952F5"),
        (0.50, "#AD1457"),
        (0.75, "#F72585"),
        (0.90, "#FF66B3"),
        (1.00, "#FFD4F0"),
    ],
)

wavefunction_cmap = LinearSegmentedColormap.from_list(
    "wavefunction_gradient",
    [
        (0.00, "#031B4E"),
        (0.25, "#0050C8"),
        (0.50, "#0070EB"),
        (0.75, "#14B5FF"),
        (1.00, "#A6FAFF"),
    ],
)

hamiltonian_cmap = LinearSegmentedColormap.from_list(
    "hamiltonian_gradient",
    [
        (0.00, "#1E0438"),
        (0.25, "#4361EE"),
        (0.50, "#7C3AED"),
        (0.75, "#A855F7"),
        (1.00, "#F3E8FF"),
    ],
)

spatial_overlap_cmap = LinearSegmentedColormap.from_list(
    "spatial_overlap_smooth",
    [
        (0.00, "#0d1117"),  # Dark background (0 overlap = quiet)
        (0.20, "#1c1445"),  # Deep navy-violet
        (0.45, "#4361EE"),  # Royal Indigo
        (0.70, "#7952F5"),  # Electric Purple
        (0.88, "#FF66B3"),  # Vibrant Rose Pink
        (1.00, "#00FFEE"),  # Glowing Electric Cyan (1.0 peak)
    ],
)

temporal_overlap_cmap = spatial_overlap_cmap
wavefunction_overlap_cmap = spatial_overlap_cmap
hamiltonian_density_cmap = spatial_overlap_cmap

cross_overlap_cmap = LinearSegmentedColormap.from_list(
    "cross_overlap_diverging",
    [
        (0.00, "#F72585"),  # -1.0 : Vibrant Neon Rose Pink
        (0.25, "#7952F5"),  # -0.5 : Electric Purple
        (0.50, "#161b22"),  #  0.0 : Neutral Dark Slate
        (0.75, "#0A95EB"),  # +0.5 : Vivid Sky Blue
        (1.00, "#00FFEE"),  # +1.0 : Bright Electric Cyan
    ],
)

temporal_cmap = cross_overlap_cmap

# Semantic Colormap Aliases (Uppercase Constants)
TEMPORAL_POD_CMAP: Final[LinearSegmentedColormap] = temporal_pod_cmap
SPATIAL_POD_CMAP: Final[LinearSegmentedColormap] = spatial_pod_cmap
WAVEFUNCTION_CMAP: Final[LinearSegmentedColormap] = wavefunction_cmap
HAMILTONIAN_CMAP: Final[LinearSegmentedColormap] = hamiltonian_cmap
SPATIAL_OVERLAP_CMAP: Final[LinearSegmentedColormap] = spatial_overlap_cmap
TEMPORAL_OVERLAP_CMAP: Final[LinearSegmentedColormap] = temporal_overlap_cmap
WAVEFUNCTION_OVERLAP_CMAP: Final[LinearSegmentedColormap] = wavefunction_overlap_cmap
HAMILTONIAN_DENSITY_CMAP: Final[LinearSegmentedColormap] = hamiltonian_density_cmap
CROSS_OVERLAP_CMAP: Final[LinearSegmentedColormap] = cross_overlap_cmap
TEMPORAL_CMAP: Final[LinearSegmentedColormap] = temporal_cmap
BLUE_TO_PINK: Final[LinearSegmentedColormap] = cross_overlap_cmap

GRADIENTS: Dict[str, List[str]] = {
    "gradient_0": ["#03E8BD", "#00FFFF", "#00E8FF", "#14B5FF"],
    "gradient_1": ["#00FFEE", "#00E8FF", "#14B5FF", "#0070EB"],
    "gradient_2": ["#00E8FF", "#14B5FF", "#3A98FF", "#0070EB", "#5E17EB"],
    "gradient_3": ["#00E8FF", "#3A98FF", "#3A98FF", "#7952F5", "#5E17EB"],
    "gradient_4": ["#03E8BD", "#00E8FF", "#14B5FF", "#5280FF", "#7952F5", "#FF66B3"],
    "gradient_5": ["#00E8FF", "#14B5FF", "#5280FF", "#7952F5", "#FF66B3", "#F78166"],
    "gradient_6": ["#8A2BE2", "#FF00FF", "#F78166", "#FFA500", "#50C878"],
    "gradient_tse": ["#00E8FF", "#14B5FF", "#0070EB", "#7066FF", "#FF66B3"],
    "temporal_pod": ["#032B14", "#059669", "#00FF7F", "#31FF48", "#CCFFBD"],
    "spatial_pod": ["#3B022D", "#7952F5", "#AD1457", "#F72585", "#FF66B3", "#FFD4F0"],
    "wavefunction": ["#031B4E", "#0050C8", "#0070EB", "#14B5FF", "#A6FAFF"],
    "hamiltonian": ["#1E0438", "#4361EE", "#7C3AED", "#A855F7", "#F3E8FF"],
    "spatial_overlap": [
        "#0d1117",
        "#1c1445",
        "#4361EE",
        "#7952F5",
        "#FF66B3",
        "#00FFEE",
    ],
    "cross_overlap": ["#F72585", "#7952F5", "#161b22", "#0A95EB", "#00FFEE"],
}

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API
# -----------------------------------------------------------------------------------------------------------


def set_style() -> None:
    """
    Set global plotting style with unified fonts, sizing, and colors.

    Applies the Scriber Experience dark slate theme, configuring
    Matplotlib and Seaborn parameters to ensure consistent aesthetics across
    figures.
    """
    font_family = ["Aclonica", "DejaVu Sans", "Helvetica Neue", "Arial", "sans-serif"]

    sns.set_theme(
        style="darkgrid",
        context="notebook",
        font_scale=0.9,
        rc={
            "axes.facecolor": THEME_BG,
            "figure.facecolor": THEME_BG,
            "savefig.facecolor": THEME_BG,
            "grid.color": GRID_COLOR,
            "grid.linestyle": ":",
            "grid.alpha": 0.6,
            "text.color": TEXT_PRIMARY,
            "axes.labelcolor": TEXT_PRIMARY,
            "xtick.color": TEXT_MUTED,
            "ytick.color": TEXT_MUTED,
            "axes.edgecolor": BORDER_COLOR,
            "font.family": "sans-serif",
            "font.sans-serif": font_family,
        },
    )

    plt.rcParams.update(
        {
            "figure.figsize": (9, 5),
            "figure.dpi": 150,
            "savefig.dpi": 200,
            "font.family": "sans-serif",
            "font.sans-serif": font_family,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.titlepad": 10,
            "axes.labelsize": 11,
            "axes.labelweight": "normal",
            "xtick.labelsize": 9.5,
            "ytick.labelsize": 9.5,
            "legend.fontsize": 9.5,
            "legend.title_fontsize": 10,
            "legend.frameon": True,
            "legend.facecolor": CARD_BG,
            "legend.edgecolor": BORDER_COLOR,
            "legend.framealpha": 0.85,
            "lines.linewidth": 2.5,
        }
    )

    plt.rcParams["axes.prop_cycle"] = plt.cycler(
        color=[
            PROJECT_COLORS["blue_light"],
            PROJECT_COLORS["purple_light"],
            PROJECT_COLORS["pink_pink"],
            PROJECT_COLORS["green_neon"],
            PROJECT_COLORS["cyan_light"],
            PROJECT_COLORS["yellow_orange"],
        ]
    )


# Alias for compatibility with notebook style invocations
_apply_style = set_style
set_style()


def get_colormap(name: str = "gradient_tse") -> LinearSegmentedColormap:
    """
    Create a Matplotlib colormap from a named gradient or semantic identifier.

    Parameters
    ----------
    name : str, default='gradient_tse'
        Name of the gradient (e.g., 'gradient_tse', 'spatial_overlap', 'cross_overlap').

    Returns
    -------
    LinearSegmentedColormap
        The requested colormap instance.
    """
    named_colormaps: Dict[str, LinearSegmentedColormap] = {
        "temporal_pod": TEMPORAL_POD_CMAP,
        "spatial_pod": SPATIAL_POD_CMAP,
        "wavefunction": WAVEFUNCTION_CMAP,
        "hamiltonian": HAMILTONIAN_CMAP,
        "spatial_overlap": SPATIAL_OVERLAP_CMAP,
        "temporal_overlap": TEMPORAL_OVERLAP_CMAP,
        "cross_overlap": CROSS_OVERLAP_CMAP,
        "temporal": TEMPORAL_CMAP,
    }
    if name in named_colormaps:
        return named_colormaps[name]
    colors = GRADIENTS.get(name, GRADIENTS["gradient_tse"])
    return LinearSegmentedColormap.from_list(name, colors)


def get_comparison_colors(quantity: str) -> Tuple[str, str]:
    """
    Return (true_color, learned_color) for a given physical quantity.

    Parameters
    ----------
    quantity : str
        Name of the physical quantity (e.g. 'potential', 'wavefunctions', 'energy',
        'density', 'order_parameter').

    Returns
    -------
    Tuple[str, str]
        Tuple containing (ground_truth_color, learned_color) hex codes.
    """
    key = quantity.lower().strip()
    if key in ("psi", "wavefunction", "wavefunctions", "eigenfunctions"):
        key = "wavefunctions"
    elif key in ("energy", "energies", "eigenvalues", "energy_eigenvalues"):
        key = "energy"
    elif key in (
        "density",
        "densities",
        "prob_density",
        "probability_density",
        "probability_densities",
    ):
        key = "density"
    elif key in ("potential", "v"):
        key = "potential"

    palette = COMPARISON_PALETTE.get(
        key, {"true": COLOR_TRUE, "learned": COLOR_LEARNED}
    )
    return palette["true"], palette["learned"]


def get_node_colors(
    adjacency: NDArray[np.floating],
    values: Optional[NDArray[np.floating]] = None,
    cmap_name: str = "gradient_tse",
) -> NDArray[Any]:
    """
    Generate colors for network nodes based on values or node degrees.

    Parameters
    ----------
    adjacency : NDArray
        Adjacency matrix of the graph.
    values : NDArray, optional
        Values to color nodes by. If None, colors by node degree.
    cmap_name : str, default='gradient_tse'
        Name of the gradient colormap to use.

    Returns
    -------
    NDArray
        Array of RGBA color values for each node.
    """
    G = nx.from_numpy_array(adjacency)
    if values is None:
        values = np.array([d for _, d in G.degree()], dtype=float)

    if np.max(values) == np.min(values):
        norm_values = np.linspace(0, 1, len(values))
    else:
        norm_values = (values - np.min(values)) / (np.max(values) - np.min(values))

    cmap = get_colormap(cmap_name)
    return cmap(norm_values)


def plot_network(
    adjacency: NDArray[np.floating],
    node_colors: Optional[NDArray[Any]] = None,
    node_values: Optional[NDArray[np.floating]] = None,
    pos: Optional[Dict[Any, NDArray[np.floating]]] = None,
    cmap_name: str = "gradient_tse",
    title: str = "Network Topology",
    save_path: Optional[str] = None,
    apply_aclonica: bool = True,
) -> None:
    """
    Visualize the oscillator network structure with The Scriber Experience styling.

    Parameters
    ----------
    adjacency : NDArray
        Adjacency matrix of the network.
    node_colors : NDArray, optional
        Precomputed colors for nodes. Takes precedence over node_values.
    node_values : NDArray, optional
        Values to color nodes by (mapped via cmap_name). If both node_colors
        and node_values are None, colors by degree.
    pos : Dict, optional
        Node positions dictionary. If None, uses spring layout.
    cmap_name : str, default='gradient_tse'
        Name of the gradient theme to use.
    title : str, default='Network Topology'
        Plot title.
    save_path : str, optional
        If provided, saves the plot to this file path.
    apply_aclonica : bool, default=True
        Whether to apply Aclonica text styling.
    """
    set_style()
    G = nx.from_numpy_array(adjacency)

    if pos is None:
        pos = nx.spring_layout(G, seed=27)

    fig, ax = plt.subplots(figsize=(10, 8), facecolor=THEME_BG)
    ax.set_facecolor(THEME_BG)

    if node_colors is None:
        node_colors = get_node_colors(
            adjacency, values=node_values, cmap_name=cmap_name
        )

    nx.draw_networkx_edges(
        G, pos, ax=ax, alpha=0.35, edge_color=BORDER_COLOR, width=1.2
    )
    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        node_color=node_colors,
        node_size=500,
        edgecolors=BORDER_COLOR,
        linewidths=1.2,
    )

    ax.set_title(title, fontsize=15, fontweight="bold", pad=12, color=TEXT_PRIMARY)
    ax.axis("off")

    if apply_aclonica:
        _apply_aclonica_font(ax)

    if save_path:
        os.makedirs(
            os.path.dirname(save_path) if os.path.dirname(save_path) else ".",
            exist_ok=True,
        )
        plt.savefig(
            save_path,
            bbox_inches="tight",
            dpi=200,
            facecolor=THEME_BG,
        )
        plt.close(fig)
    else:
        plt.show()


def plot_distributions(
    omega: NDArray[np.floating],
    theta_0: Optional[NDArray[np.floating]] = None,
    cmap_name: str = "gradient_tse",
    save_path: Optional[str] = None,
    apply_aclonica: bool = True,
) -> None:
    """
    Plot histograms of natural frequencies and initial phases with The Scriber Experience styling.

    Parameters
    ----------
    omega : NDArray
        Natural frequencies array.
    theta_0 : NDArray, optional
        Initial phases array.
    cmap_name : str, default='gradient_tse'
        Name of the gradient theme to use for the primary histogram.
    save_path : str, optional
        If provided, saves the plot to this file path.
    apply_aclonica : bool, default=True
        Whether to apply Aclonica font styling to the plot.
    """
    set_style()
    n_plots = 2 if theta_0 is not None else 1
    fig, axes = plt.subplots(1, n_plots, figsize=(6.5 * n_plots, 5), facecolor=THEME_BG)

    if n_plots == 1:
        axes = [axes]

    # Plot omega
    sns.histplot(
        omega,
        kde=True,
        ax=axes[0],
        color=PROJECT_COLORS["blue_light"],
        alpha=0.75,
        edgecolor=BORDER_COLOR,
        linewidth=0.8,
    )
    axes[0].set_title(
        "Natural Frequency Distribution",
        fontsize=13,
        fontweight="bold",
        pad=10,
        color=TEXT_PRIMARY,
    )
    axes[0].set_xlabel(r"$\omega_i$", fontsize=11, color=TEXT_PRIMARY)
    axes[0].set_ylabel("Count", fontsize=11, color=TEXT_PRIMARY)

    if theta_0 is not None:
        sns.histplot(
            theta_0,
            kde=True,
            ax=axes[1],
            color=PROJECT_COLORS["purple_light"],
            alpha=0.75,
            edgecolor=BORDER_COLOR,
            linewidth=0.8,
        )
        axes[1].set_title(
            "Initial Phase Distribution",
            fontsize=13,
            fontweight="bold",
            pad=10,
            color=TEXT_PRIMARY,
        )
        axes[1].set_xlabel(r"$\theta_i(0)$", fontsize=11, color=TEXT_PRIMARY)
        axes[1].set_ylabel("Count", fontsize=11, color=TEXT_PRIMARY)

    if apply_aclonica:
        for ax in axes:
            _apply_aclonica_font(ax)

    plt.tight_layout()

    if save_path:
        os.makedirs(
            os.path.dirname(save_path) if os.path.dirname(save_path) else ".",
            exist_ok=True,
        )
        plt.savefig(
            save_path,
            dpi=200,
            bbox_inches="tight",
            facecolor=THEME_BG,
        )
        plt.close(fig)
    else:
        plt.show()


def plot_order_parameter(
    times: NDArray[np.floating],
    r_values: NDArray[np.floating],
    title: str = "Order Parameter Over Time",
    save_path: Optional[str] = None,
    apply_aclonica: bool = True,
    gradient_fill: bool = True,
) -> None:
    """
    Plot the Kuramoto order parameter R(t) with The Scriber Experience styling.

    Parameters
    ----------
    times : NDArray
        Time points of the simulation, shape (n_steps,).
    r_values : NDArray
        Order parameter values R(t) in [0, 1], shape (n_steps,).
        Must match the length of `times`.
    title : str, default='Order Parameter Over Time'
        Plot title.
    save_path : str, optional
        If provided, saves the plot to this file path.
    apply_aclonica : bool, default=True
        Whether to attempt applying the Aclonica font.
    gradient_fill : bool, default=True
        Whether to shade the area under the R(t) curve with an accent fill.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If `times` and `r_values` have mismatched lengths.
    """
    if len(times) != len(r_values):
        raise ValueError(
            f"Shape mismatch: times has {len(times)} points but "
            f"r_values has {len(r_values)} points."
        )

    set_style()
    fig, ax = plt.subplots(figsize=(9, 5), facecolor=THEME_BG)

    ax.plot(
        times,
        r_values,
        color=PROJECT_COLORS["cyan_light"],
        linewidth=2.5,
        label=r"$R(t)$",
    )

    if gradient_fill:
        ax.fill_between(
            times,
            r_values,
            alpha=0.30,
            color=PROJECT_COLORS["purple_deep"],
        )

    ax.set_title(title, fontsize=13, fontweight="bold", pad=10, color=TEXT_PRIMARY)
    ax.set_xlabel("Time (t)", fontsize=11, color=TEXT_PRIMARY)
    ax.set_ylabel(r"Order Parameter $R(t)$", fontsize=11, color=TEXT_PRIMARY)
    ax.set_ylim(-0.02, 1.05)

    if apply_aclonica:
        _apply_aclonica_font(ax)

    if save_path:
        os.makedirs(
            os.path.dirname(save_path) if os.path.dirname(save_path) else ".",
            exist_ok=True,
        )
        plt.savefig(
            save_path,
            dpi=200,
            bbox_inches="tight",
            facecolor=THEME_BG,
        )
        plt.close(fig)
    else:
        plt.show()


def plot_semantic_colormaps(
    *,
    out_path: Optional[str | Path] = None,
) -> plt.Figure:
    """
    Render a visual demonstration of the project semantic color gradients and diagnostic colormaps.

    Parameters
    ----------
    out_path : str | Path, optional
        If provided, save the figure to the specified path.

    Returns
    -------
    plt.Figure
        The created Matplotlib figure.
    """
    set_style()

    palettes = [
        ("Temporal POD (Green Gradient)", TEMPORAL_POD_CMAP),
        ("Spatial POD (Magenta Gradient)", SPATIAL_POD_CMAP),
        ("Wavefunctions (Blue Gradient)", WAVEFUNCTION_CMAP),
        ("Hamiltonian (Purple Gradient)", HAMILTONIAN_CMAP),
        ("Spatial Overlap [0, 1]", SPATIAL_OVERLAP_CMAP),
        ("Temporal Overlap [0, 1]", TEMPORAL_OVERLAP_CMAP),
        ("Wavefunction Overlap [0, 1]", WAVEFUNCTION_OVERLAP_CMAP),
        ("Hamiltonian Density [0, 1]", HAMILTONIAN_DENSITY_CMAP),
        ("Temporal Modal V [-1, 1]", TEMPORAL_CMAP),
        ("Cross Overlap M [-1, 1]", CROSS_OVERLAP_CMAP),
    ]

    fig, axes = plt.subplots(
        len(palettes),
        1,
        figsize=(10, 7.5),
        facecolor=THEME_BG,
        constrained_layout=True,
    )

    gradient = np.linspace(0, 1, 256).reshape(1, -1)

    for ax, (label, cmap) in zip(axes, palettes, strict=True):
        ax.imshow(gradient, aspect="auto", cmap=cmap)
        ax.set_axis_off()
        ax.text(
            -0.02,
            0.5,
            label,
            transform=ax.transAxes,
            va="center",
            ha="right",
            fontsize=9.5,
            fontweight="bold",
            color=TEXT_PRIMARY,
        )

    fig.suptitle(
        "Semantic & Diagnostic Color Gradients (Visual-Memory Convention)",
        fontsize=13,
        fontweight="bold",
        color=TEXT_PRIMARY,
    )

    if out_path:
        out_p = Path(out_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_p, dpi=200, bbox_inches="tight", facecolor=THEME_BG)

    return fig


# -----------------------------------------------------------------------------------------------------------
# 2️⃣ Internal Logic & Helpers
# -----------------------------------------------------------------------------------------------------------


def _apply_aclonica_font(ax: plt.Axes) -> None:
    """
    Apply Aclonica font to axes elements if available.

    Falls back to system sans-serif if Aclonica is not installed.

    Parameters
    ----------
    ax : plt.Axes
        The axes object to apply font styling to.

    Returns
    -------
    None
    """
    try:
        font_names = {f.name for f in fm.fontManager.ttflist}
        if "Aclonica" not in font_names:
            for font_path in findSystemFonts():
                if "Aclonica" in font_path:
                    fm.fontManager.addfont(font_path)
                    font_names.add("Aclonica")
                    break

        if "Aclonica" in font_names:
            for element in [ax.title, ax.xaxis.label, ax.yaxis.label]:
                if element:
                    element.set_fontname("Aclonica")

            for tick_label in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
                if tick_label:
                    tick_label.set_fontname("Aclonica")

            legend = ax.get_legend()
            if legend:
                for text in legend.get_texts():
                    text.set_fontname("Aclonica")
                if legend.get_title():
                    legend.get_title().set_fontname("Aclonica")
        else:
            warnings.warn(
                "📝 Aclonica not found. Using system sans-serif font."
                "Download from https://www.dafont.com/aclonica.font for full aesthetic.",
                stacklevel=2,
            )
    except Exception:
        pass  # Silent failover


def _plot_gradient_bar(
    ax: plt.Axes,
    x: float,
    height: float,
    width: float,
    cmap: mcolors.Colormap,
    label: str | None = None,
    *,
    n_segments: int = 48,
    zorder: int = 3,
    edgecolor: str | None = BORDER_COLOR,
    linewidth: float = 0.8,
    alpha_bottom: float = 0.70,
    alpha_top: float = 0.95,
) -> None:
    """
    Draw a bar with a smooth, golden-ratio scaled gradient fill.

    Parameters
    ----------
    ax : plt.Axes
        Axes to draw on.
    x : float
        X-coordinate of bar center.
    height : float
        Height of the bar.
    width : float
        Width of the bar.
    cmap : mcolors.Colormap
        Colormap used for gradient.
    label : str, optional
        Legend label for the bar.
    n_segments : int, default=48
        Number of vertical segments for gradient rendering.
    zorder : int, default=3
        Drawing layer order.
    edgecolor : str, optional
        Boundary border color.
    linewidth : float, default=0.8
        Border stroke width.
    alpha_bottom : float, default=0.70
        Bottom opacity.
    alpha_top : float, default=0.95
        Top opacity.
    """
    if height == 0:
        return

    segment_height = height / n_segments
    for i in range(n_segments):
        t = i / (n_segments - 1) if n_segments > 1 else 1.0
        t_scaled = t ** (1.0 / GOLDEN_RATIO)
        color = cmap(t_scaled)
        r, g, b, _ = mcolors.to_rgba(color)
        alpha = alpha_bottom + (alpha_top - alpha_bottom) * t_scaled

        ax.bar(
            x,
            segment_height,
            width=width,
            bottom=i * segment_height,
            color=(r, g, b, alpha),
            edgecolor="none",
            zorder=zorder,
        )

    if edgecolor is not None:
        rect = ax.bar(
            x,
            height,
            width=width,
            facecolor="none",
            edgecolor=edgecolor,
            linewidth=linewidth,
            zorder=zorder + 1,
        )
        if label:
            rect.set_label(label)
    elif label:
        ax.patches[-1].set_label(label)


def _add_lambda_row(
    fig: plt.Figure,
    lambdas: Dict[str, float] | None,
    *,
    ax: plt.Axes | None = None,
    y: float | None = None,
    x: float | None = None,
    fontsize: float | None = None,
) -> Text | None:
    """
    Render loss-weight or parameter dictionary as a sleek glassmorphic pill badge.

    Parameters
    ----------
    fig : plt.Figure
        Target figure.
    lambdas : Dict[str, float], optional
        Mapping of parameter / weight names to float values.
    ax : plt.Axes, optional
        Reference axes for relative placement.
    y : float, optional
        Explicit Y coordinate in figure space.
    x : float, optional
        Explicit X coordinate in figure space.
    fontsize : float, optional
        Font size for text badge.

    Returns
    -------
    Text or None
        The created Matplotlib Text artist, or None if lambdas is empty.
    """
    if not lambdas:
        return None

    lambda_str = "    ".join(rf"$\lambda_{{{k}}} = {v:g}$" for k, v in lambdas.items())

    if ax is not None:
        bbox = ax.get_position()
        lambda_x = x if x is not None else (bbox.x0 + bbox.x1) / 2.0
        lambda_y = y if y is not None else (bbox.y1 - 0.03)
    else:
        lambda_x = x if x is not None else 0.5
        if y is not None:
            lambda_y = y
        else:
            suptitle = getattr(fig, "_suptitle", None)
            if suptitle is not None:
                _, title_y = suptitle.get_position()
                lambda_y = title_y - 0.05
            else:
                lambda_y = 0.94

    fs = fontsize if fontsize is not None else 9.5

    return fig.text(
        lambda_x,
        lambda_y,
        lambda_str,
        ha="center",
        va="center",
        fontsize=fs,
        color=TEXT_PRIMARY,
        bbox={
            "boxstyle": "round,pad=0.5,rounding_size=0.3",
            "facecolor": CARD_BG,
            "edgecolor": BORDER_COLOR,
            "alpha": 0.90,
            "linewidth": 1.0,
        },
        transform=fig.transFigure,
    )


def _add_spike_lines(
    ax: plt.Axes,
    spike_epochs: Sequence[int],
    *,
    color: str = TEXT_MUTED,
    linestyle: str = "--",
    linewidth: float = 1.5,
    alpha: float = 0.75,
    label: str = "Spike / Transition",
) -> None:
    """
    Draw vertical dashed indicator lines at designated transition points.

    Parameters
    ----------
    ax : plt.Axes
        Target axes to annotate.
    spike_epochs : Sequence[int]
        Indices or epochs where transitions occur.
    color : str, default=TEXT_MUTED
        Line color.
    linestyle : str, default='--'
        Line style.
    linewidth : float, default=1.5
        Line width.
    alpha : float, default=0.75
        Line opacity.
    label : str, default='Spike / Transition'
        Legend label for the indicator.
    """
    if not spike_epochs:
        return
    for idx, ep in enumerate(spike_epochs):
        lbl = label if idx == 0 else None
        ax.axvline(
            x=ep,
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
            alpha=alpha,
            label=lbl,
            zorder=2,
        )


def detect_loss_spikes(
    epochs: Sequence[int],
    series: Sequence[float] | NDArray[Any],
    *,
    threshold: float = 1.0,
    method: str = "log_diff",
    direction: str = "both",
    min_epoch_gap: int = 200,
) -> List[int]:
    """
    Identify epoch numbers where significant spikes or transitions occur in a time series.

    Parameters
    ----------
    epochs : Sequence[int]
        Sequence of epoch numbers or time points.
    series : Sequence[float] | NDArray
        Values across epochs.
    threshold : float, default=1.0
        Sensitivity threshold for detecting a transition.
    method : str, default='log_diff'
        Detection strategy: 'log_diff', 'relative', or 'zscore'.
    direction : str, default='both'
        Direction of change: 'both', 'positive'/'up', or 'negative'/'down'.
    min_epoch_gap : int, default=200
        Minimum distance between successive detected points.

    Returns
    -------
    List[int]
        List of epoch numbers where significant transitions were detected.
    """
    if len(epochs) < 2 or len(series) < 2:
        return []

    if hasattr(series, "detach"):
        s = series.detach().cpu().numpy().astype(float)  # type: ignore[union-attr]
    elif isinstance(series, np.ndarray):
        s = series.astype(float)
    else:
        s = np.array(series, dtype=float)

    eps = 1e-15
    s_safe = np.maximum(s, eps)
    ep_arr = np.array(epochs)
    dir_mode = direction.lower().strip()

    if method == "log_diff":
        log_s = np.log10(s_safe)
        diffs = np.diff(log_s)
        if dir_mode in ("positive", "up", "increase"):
            spike_indices = np.where(diffs >= threshold)[0] + 1
        elif dir_mode in ("negative", "down", "decrease"):
            spike_indices = np.where(diffs <= -threshold)[0] + 1
        else:
            spike_indices = np.where(np.abs(diffs) >= threshold)[0] + 1
    elif method == "relative":
        rel_diffs = np.diff(s_safe) / s_safe[:-1]
        if dir_mode in ("positive", "up", "increase"):
            spike_indices = np.where(rel_diffs >= threshold)[0] + 1
        elif dir_mode in ("negative", "down", "decrease"):
            spike_indices = np.where(rel_diffs <= -threshold)[0] + 1
        else:
            spike_indices = np.where(np.abs(rel_diffs) >= threshold)[0] + 1
    elif method == "zscore":
        diffs = np.diff(s_safe)
        mean_d = np.mean(diffs)
        std_d = np.std(diffs) + eps
        z = (diffs - mean_d) / std_d
        if dir_mode in ("positive", "up", "increase"):
            spike_indices = np.where(z >= threshold)[0] + 1
        elif dir_mode in ("negative", "down", "decrease"):
            spike_indices = np.where(z <= -threshold)[0] + 1
        else:
            spike_indices = np.where(np.abs(z) >= threshold)[0] + 1
    else:
        raise ValueError(
            f"Unknown spike detection method: {method}. Choose from 'log_diff', 'relative', 'zscore'."
        )

    detected_epochs: List[int] = []
    last_ep = -1000000
    for idx in spike_indices:
        ep = int(ep_arr[idx])
        if ep - last_ep >= min_epoch_gap:
            detected_epochs.append(ep)
            last_ep = ep

    return detected_epochs


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests / example usage
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Sanity check for visualization tools and colormaps."""
    print("💨 Running visualization smoke tests...")

    # 1. Verify all semantic colormaps exist and are callable
    all_colormaps = {
        "temporal_pod_cmap": (temporal_pod_cmap, TEMPORAL_POD_CMAP),
        "spatial_pod_cmap": (spatial_pod_cmap, SPATIAL_POD_CMAP),
        "wavefunction_cmap": (wavefunction_cmap, WAVEFUNCTION_CMAP),
        "hamiltonian_cmap": (hamiltonian_cmap, HAMILTONIAN_CMAP),
        "spatial_overlap_cmap": (spatial_overlap_cmap, SPATIAL_OVERLAP_CMAP),
        "temporal_overlap_cmap": (temporal_overlap_cmap, TEMPORAL_OVERLAP_CMAP),
        "wavefunction_overlap_cmap": (
            wavefunction_overlap_cmap,
            WAVEFUNCTION_OVERLAP_CMAP,
        ),
        "hamiltonian_density_cmap": (
            hamiltonian_density_cmap,
            HAMILTONIAN_DENSITY_CMAP,
        ),
        "temporal_cmap": (temporal_cmap, TEMPORAL_CMAP),
        "cross_overlap_cmap": (cross_overlap_cmap, CROSS_OVERLAP_CMAP),
    }
    for name, (cmap_obj, alias_obj) in all_colormaps.items():
        assert isinstance(
            cmap_obj, mpl.colors.Colormap
        ), f"{name} must be an instance of mpl.colors.Colormap"
        assert cmap_obj is alias_obj, f"{name} must match its alias constant"
        for val in (0.0, 0.5, 1.0):
            rgba = cmap_obj(val)
            assert (
                isinstance(rgba, tuple) and len(rgba) == 4
            ), f"{name}({val}) must return a 4-channel RGBA tuple"
            assert all(
                0.0 <= c <= 1.0 for c in rgba
            ), f"{name}({val}) channel values must be in [0.0, 1.0]"

    # 2. Test get_comparison_colors
    t_col, l_col = get_comparison_colors("potential")
    assert t_col == COLOR_POTENTIAL_TRUE
    assert l_col == COLOR_POTENTIAL_LEARNED

    # 3. Test Network data & plot
    n = 20
    adj = np.ones((n, n)) - np.eye(n)
    omega = np.random.normal(0, 1, n)
    theta_0 = np.random.uniform(0, 2 * np.pi, n)

    # 4. Order parameter time-series data
    times = np.linspace(0, 100, 500)
    r_values = 0.7 + 0.2 * np.sin(0.1 * times) + 0.05 * np.random.randn(500)

    os.makedirs("plots/tests", exist_ok=True)

    plot_network(adj, node_values=omega, save_path="plots/tests/test_network.png")
    assert os.path.exists("plots/tests/test_network.png")

    plot_distributions(omega, theta_0, save_path="plots/tests/test_dist.png")
    assert os.path.exists("plots/tests/test_dist.png")

    plot_order_parameter(times, r_values, save_path="plots/tests/test_order_param.png")
    assert os.path.exists("plots/tests/test_order_param.png")

    plot_semantic_colormaps(out_path="plots/tests/test_colormaps.png")
    assert os.path.exists("plots/tests/test_colormaps.png")

    print("\n✅ Visualization smoke tests passed.")
    print("\n📁 Saved plots to plots/tests/")
    for fn in os.listdir("plots/tests"):
        print(f"   └─ {fn}")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Main entry point for visualization module."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
