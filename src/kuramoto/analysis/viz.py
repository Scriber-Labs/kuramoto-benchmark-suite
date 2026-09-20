"""
viz.py

Visualization tools for Kuramoto oscillator networks and distributions.
Implements custom gradient themes and Seaborn-based plotting.

Author: Eigenscribe
Date: May 2026
Last Updated: September 2026
"""

from __future__ import annotations

import os
import warnings
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.font_manager import FontProperties, findSystemFonts
from typing import Dict, List, Optional, Any
from numpy.typing import NDArray

# -----------------------------------------------------------------------------------------------------------
# 🎨 Constants & Themes
# -----------------------------------------------------------------------------------------------------------

SCRIBER_PALETTE = {
    "bg_deep": "#0D1117",
    "bg_panel": "#161B22",
    "accent_cyan": "#14B5FF",
    "accent_teal": "#00C8FF",
    "accent_purple": "#7952F5",
    "accent_indigo": "#7066FF",
    "text_primary": "#C9D1D9",
    "text_muted": "#8B949E",
    "grid": "#84B5CC",
}

GRADIENTS: Dict[str, List[str]] = {
    "gradient_0": ["#03E8BD", "#00FFFF", "#00E8FF", "#14B5FF"],
    "gradient_1": ["#00FFEE", "#00E8FF", "#14B5FF", "#0070EB"],
    "gradient_2": ["#00E8FF", "#14B5FF", "#3A98FF", "#0070EB", "#5E17EB"],
    "gradient_3": ["#00E8FF", "#3A98FF", "#3A98FF", "#7952F5", "#5E17EB"],
    "gradient_4": ["03E8BD", "#00E8FF", "#14B5FF", "#5280FF", "#7952F5", "#FF66B3"],
    "gradient_5": ["#00E8FF", "#14B5FF", "#5280FF", "#7952F5", "#FF66B3", "#F78166"],
    "gradient_6": ["#8A2BE2", "#FF00FF", "#F78166", "#FFA500", "#50C878"],
    "gradient_tse": ["#00E8FF", "#14B5FF", "#0070EB", "#7066FF", "#FF66B3"],

}

def get_colormap(name: str = "gradient_tse")  -> LinearSegmentedColormap:
    """
    Create a Matplotlib colormap from a named gradient.

    Parameters
    ----------
    name : str
        Name of the gradient (e.g., 'gradient_tse').

    Returns
    -------
    LinearSegmentedColormap
        The requested colormap.
    """
    colors = GRADIENTS.get(name, GRADIENTS["gradient_tse"])
    return LinearSegmentedColormap.from_list(name, colors)

def get_node_colors(
    adjacency: NDArray[np.floating],
    values: Optional[NDArray[np.floating]] = None,
    cmap_name: str = "gradient_tse"
) -> NDArray[Any]:
    """
    Generate colors for nodes based on values or degree.

    Parameters
    ----------
    adjacency : NDArray
        Adjacency matrix.
    values : NDArray, optional
        Values to color by. If None, uses node degrees.
    cmap_name : str
        Name of the gradient theme.

    Returns
    -------
    NDArray
        Array of RGBA colors.
    """
    G = nx.from_numpy_array(adjacency)
    if values is None:
        # Use degrees if no values provided
        values = np.array([d for n, d in G.degree()], dtype=float)
    
    # Normalize values to [0, 1] for colormap
    if np.max(values) == np.min(values):
        # Fallback to linear distribution if all values are identical
        norm_values = np.linspace(0, 1, len(values))
    else:
        norm_values = (values - np.min(values)) / (np.max(values) - np.min(values))
    
    cmap = get_colormap(cmap_name)
    return cmap(norm_values)

def _apply_aclonica_font(
        ax: plt.Axes,
) -> None:
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

    Raises
    ------
    Warning
        Emits warning if Aclonica font not found in system fonts.

    Notes
    -----
    Searches system font paths for 'Aclonica' and applies to:
    - Axis titles (x and y labels)
    - Plot title
    - Tick labels (both axes)
    """
    try:
        font_found = False
        for font_path in findSystemFonts():
            if 'Aclonica' in font_path:
                font_found = True
                break

        if font_found:
            for element in [ax.title, ax.xaxis.label, ax.yaxis.label]:
                if element:
                    element.set_fontname('Aclonica')

            for tick_label in ax.get_xticklabels() + ax.get_yticklabels():
                tick_label.set_fontname('Aclonica')
        else:
            warnings.warn(
                "📝 Aclonica not found. Using system sans-serif font."
                "Download from https://www.dafont.com/aclonica.font for full aesthetic.",
                stacklevel=2
            )
    except Exception:
        pass  # Silent failover

def set_style() -> None:
    """Apply the project's visual style using Seaborn."""
    sns.set_theme(style="darkgrid", palette="muted")

    plt.rcParams.update({
        'figure.facecolor': SCRIBER_PALETTE["bg_deep"],
        'figure.figsize': (10, 6),
        'axes.facecolor': SCRIBER_PALETTE["bg_panel"],
        'axes.edgecolor': SCRIBER_PALETTE["accent_purple"],
        'axes.linewidth': 1.5,
        'axes.titlecolor': SCRIBER_PALETTE["accent_cyan"],
        'axes.labelcolor': SCRIBER_PALETTE["text_primary"],
        'font.family': ['sans-serif'],
        'text.color': SCRIBER_PALETTE["text_primary"],
        'axes.labelweight': 'normal',
        'xtick.color': SCRIBER_PALETTE["accent_cyan"],
        'ytick.color': SCRIBER_PALETTE["accent_cyan"],
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.width': 1.5,
        'ytick.major.width': 1.5,
        'grid.color': SCRIBER_PALETTE["grid"],
        'grid.alpha': 0.25,
        'grid.linestyle': '--',
        'grid.linewidth': 1.0,
        'lines.linewidth': 2.5,
        'lines.color': SCRIBER_PALETTE["accent_cyan"],
        'lines.solid_capstyle': 'round',
        'scatter.marker': 'o',
        'scatter.edgecolors': SCRIBER_PALETTE["accent_purple"],
        'legend.facecolor': SCRIBER_PALETTE["accent_cyan"],
        'legend.edgecolor': SCRIBER_PALETTE["accent_purple"],
        'legend.framealpha': 0.7,
        'legend.fontsize': 'medium',
        'legend.title_fontsize': 'medium',
        'savefig.facecolor': SCRIBER_PALETTE["bg_deep"],
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.transparent': False,
    })

    plt.rcParams['axes.prop_cycle'] = plt.cycler(
        color=[
            SCRIBER_PALETTE["accent_cyan"],
            SCRIBER_PALETTE["accent_purple"],
            SCRIBER_PALETTE["accent_teal"],
            SCRIBER_PALETTE["accent_indigo"],
        ]
    )

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core definitions
# -----------------------------------------------------------------------------------------------------------

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
        Node positions. If None, uses spring layout.
    cmap_name : str
        Name of the gradient theme to use.
    title : str
        Plot title.
    save_path : str, optional
        If provided, saves the plot to this path.
    apply_aclonica : bool
        Whether to apply Aclonica text style. Default set to True.
    """
    set_style()
    G = nx.from_numpy_array(adjacency)
    
    if pos is None:
        pos = nx.spring_layout(G, seed=27)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    if node_colors is None:
        node_colors = get_node_colors(adjacency, values=node_values, cmap_name=cmap_name)

    nx.draw_networkx_edges(G, pos, alpha=0.2, edge_color=SCRIBER_PALETTE["text_muted"])
    nodes = nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors, 
        node_size=500,
        edgecolors=SCRIBER_PALETTE["accent_purple"],
        linewidths=1.5
    )
    
    plt.title(title, fontsize=16)
    plt.axis("off")

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
            dpi=300,
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
        Natural frequencies.
    theta_0 : NDArray, optional
        Initial phases.
    cmap_name : str
        Name of the gradient theme to use for the primary histogram.
    save_path : str, optional
        If provided, saves the plot to this path.
    apply_aclonica : bool
        Whether to apply AcLonica font styling to the plot. Default set to True.
    """
    set_style()
    n_plots = 2 if theta_0 is not None else 1
    fig, axes = plt.subplots(1, n_plots, figsize=(6 * n_plots, 5))
    
    if n_plots == 1:
        axes = [axes]

    cmap = get_colormap(cmap_name)
        
    # Plot omega
    sns.histplot(
        omega,
        kde=True,
        ax=axes[0],
        color=SCRIBER_PALETTE["accent_cyan"],
        alpha=0.8
    )
    axes[0].set_title("Natural Frequency Distribution", fontsize=14)
    axes[0].set_xlabel(r"$\omega_i$", fontsize=12)
    axes[0].set_ylabel("Count", fontsize=12)
    
    if theta_0 is not None:
        sns.histplot(
            theta_0,
            kde=True,
            ax=axes[1],
            color=SCRIBER_PALETTE["accent_cyan"],
            alpha=0.8
        )
        axes[1].set_title("Initial Phase Distribution", fontsize=14)
        axes[1].set_xlabel(r"$\theta_i(0)$", fontsize=12)
        axes[1].set_ylabel("Count", fontsize=12)

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
            dpi=300,
            bbox_inches="tight",
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
    title : str, optional
        Plot title. Defaults to "Order Parameter Over Time".
    save_path : str, optional
        If provided, saves the plot to this path. Directories are created as needed.
        If none, displays the plot interactively.
    apply_aclonica : bool, optional
        Whether to attempt applying the Aclonica font. Defaults to True.
    gradient_fill : bool, optional
        Whether to shade the area under the R(T) curve with a translucent accent color. Defaults to True.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If `times` and `r_values` have mismatched lengths.

    Notes
    -----
    The y-axis is clamped to [0, 1.1] since R(t) is bounded by construction:
    R -> 0 indicates incoherence, R -> 1 indicates full phase-locking of the ensemble.
    """

    if len(times) != len(r_values):
        raise ValueError(
            f"Shape mismatch: times has {len(times)} points but "
            f"r_values has {len(r_values)} points."
        )

    set_style()
    fig, ax = plt.subplots(figsize=(10, 6))

    cmap = get_colormap("gradient_tse")

    # Plot line with gradient effect
    line, = ax.plot(
        times,
        r_values,
        color=SCRIBER_PALETTE["accent_cyan"],
        linewidth=2.5,
    )

    if gradient_fill:
        # Add translucent gradient fill under curve
        fill_ax = ax.fill_between(
            times,
            r_values,
            alpha=0.3,
            color=SCRIBER_PALETTE["accent_purple"],
        )

    ax.set_title(title, fontsize=16)
    ax.set_xlabel("Time (t)", fontsize=12)
    ax.set_ylabel("Order parameter R(t)", fontsize=12)
    ax.set_ylim(0, 1.1)

    if apply_aclonica:
        _apply_aclonica_font(ax)

    if save_path:
        os.makedirs(
            os.path.dirname(save_path) if os.path.dirname(save_path) else ".",
            exist_ok=True,
        )
        plt.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight",
        )
        plt.close(fig)
    else:
        plt.show()

# -----------------------------------------------------------------------------------------------------------
# 4️⃣ Smoke tests / example usage
# -----------------------------------------------------------------------------------------------------------

def _run_smoke_test() -> None:
    """Sanity check for visualization tools."""
    print("💨 Running visualization smoke tests...")
    
    # Network data
    n = 20
    adj = np.ones((n, n)) - np.eye(n)
    omega = np.random.normal(0, 1, n)
    theta_0 = np.random.uniform(0, 2*np.pi, n)

    # Order parameter time-series data
    times = np.linspace(0, 100, 500)
    r_values = 0.7 + 0.2 * np.sin(0.1 * times) + 0.05 * np.random.randn(500)
    
    os.makedirs("plots/tests", exist_ok=True)
    
    # Test network plot
    plot_network(adj, node_values=omega, save_path="plots/tests/test_network.png")
    assert os.path.exists("plots/tests/test_network.png")
    
    # Test distribution plot
    plot_distributions(omega, theta_0, save_path="plots/tests/test_dist.png")
    assert os.path.exists("plots/tests/test_dist.png")

    # Test order parameter plot
    plot_order_parameter(times, r_values, save_path="plots/tests/test_order_param.png")
    assert os.path.exists("plots/tests/test_order_param.png")
    
    print("\n✅ Visualization smoke tests passed.")

# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------

def main() -> None:
    """Main entry point."""
    _run_smoke_test()

if __name__ == "__main__":
    main()
