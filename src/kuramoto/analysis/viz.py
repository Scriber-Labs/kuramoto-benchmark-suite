"""
viz.py

Visualization tools for Kuramoto oscillator networks and distributions.
Implements custom gradient themes and Seaborn-based plotting.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from matplotlib.colors import LinearSegmentedColormap
from typing import Dict, List, Optional, Any
from numpy.typing import NDArray

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ Constants & Themes
# -----------------------------------------------------------------------------------------------------------

GRADIENTS: Dict[str, List[str]] = {
    "gradient_0": ["#00FFFF", "#00E8FF"],
    "gradient_1": ["#00FFEE", "#14B5FF"],
    "gradient_2": ["#00E8FF", "#0070EB"],
    "gradient_3": ["#03E8BD", "#03B4E8", "#0355E8"],
    "gradient_4": ["#00E8FF", "#14B5FF", "#0A95EB", "#0070EB", "#5E17EB"],
    "gradient_5": ["#00E8FF", "#3A98FF", "#0A95EB", "#7952F5", "#5E17EB"],
    "gradient_6": ["#00E8FF", "#14B5FF", "#5280FF", "#7952F5", "#FF66B3"],
    "gradient_7": ["#00E8FF", "#14B5FF", "#5280FF", "#7952F5", "#FF66B3", "#F78166"],
    "vibrant": ["#8A2BE2", "#FF00FF", "#FFA500", "#50C878"],
}

def get_colormap(name: str = "gradient_4") -> LinearSegmentedColormap:
    """
    Create a Matplotlib colormap from a named gradient.

    Parameters
    ----------
    name : str
        Name of the gradient (e.g., 'gradient_4').

    Returns
    -------
    LinearSegmentedColormap
        The requested colormap.
    """
    colors = GRADIENTS.get(name, GRADIENTS["gradient_4"])
    return LinearSegmentedColormap.from_list(name, colors)

def get_node_colors(
    adjacency: NDArray[np.floating],
    values: Optional[NDArray[np.floating]] = None,
    cmap_name: str = "gradient_4"
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

def set_style() -> None:
    """Apply the project's visual style using Seaborn."""
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.titleweight"] = "bold"

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core definitions
# -----------------------------------------------------------------------------------------------------------

def plot_network(
    adjacency: NDArray[np.floating],
    node_colors: Optional[NDArray[Any]] = None,
    node_values: Optional[NDArray[np.floating]] = None,
    pos: Optional[Dict[Any, NDArray[np.floating]]] = None,
    cmap_name: str = "gradient_4",
    title: str = "Network Topology",
    save_path: Optional[str] = None
) -> None:
    """
    Visualize the oscillator network structure.

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
    """
    set_style()
    G = nx.from_numpy_array(adjacency)
    
    if pos is None:
        pos = nx.spring_layout(G, seed=42)
    
    plt.figure(figsize=(10, 8))
    
    if node_colors is None:
        node_colors = get_node_colors(adjacency, values=node_values, cmap_name=cmap_name)

    nx.draw_networkx_edges(G, pos, alpha=0.2, edge_color="gray")
    nodes = nx.draw_networkx_nodes(
        G, pos, 
        node_color=node_colors, 
        node_size=500,
        edgecolors="white",
        linewidths=1.5
    )
    
    plt.title(title)
    plt.axis("off")
    
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        plt.close()
    else:
        plt.show()

def plot_distributions(
    omega: NDArray[np.floating],
    theta_0: Optional[NDArray[np.floating]] = None,
    cmap_name: str = "gradient_3",
    save_path: Optional[str] = None
) -> None:
    """
    Plot histograms of natural frequencies and initial phases.

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
    """
    set_style()
    n_plots = 2 if theta_0 is not None else 1
    fig, axes = plt.subplots(1, n_plots, figsize=(6 * n_plots, 5))
    
    if n_plots == 1:
        axes = [axes]
        
    # Plot omega
    sns.histplot(omega, kde=True, ax=axes[0], color=GRADIENTS[cmap_name][0])
    axes[0].set_title("Natural Frequency Distribution")
    axes[0].set_xlabel(r"$\omega_i$")
    
    if theta_0 is not None:
        sns.histplot(theta_0, kde=True, ax=axes[1], color=GRADIENTS[cmap_name][-1])
        axes[1].set_title("Initial Phase Distribution")
        axes[1].set_xlabel(r"$\theta_i(0)$")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300)
        plt.close()
    else:
        plt.show()

# -----------------------------------------------------------------------------------------------------------
# 4️⃣ Smoke tests / example usage
# -----------------------------------------------------------------------------------------------------------

def _run_smoke_test() -> None:
    """Sanity check for visualization tools."""
    print("💨 Running visualization smoke tests...")
    
    # Dummy data
    n = 20
    adj = np.ones((n, n)) - np.eye(n)
    omega = np.random.normal(0, 1, n)
    theta_0 = np.random.uniform(0, 2*np.pi, n)
    
    os.makedirs("plots/tests", exist_ok=True)
    
    # Test network plot
    plot_network(adj, node_values=omega, save_path="plots/tests/test_network.png")
    assert os.path.exists("plots/tests/test_network.png")
    
    # Test distribution plot
    plot_distributions(omega, theta_0, save_path="plots/tests/test_dist.png")
    assert os.path.exists("plots/tests/test_dist.png")
    
    print("✅ Visualization smoke tests passed.")

# -----------------------------------------------------------------------------------------------------------
# 5️⃣ Entry point
# -----------------------------------------------------------------------------------------------------------

def main() -> None:
    """Main entry point."""
    _run_smoke_test()

if __name__ == "__main__":
    main()
