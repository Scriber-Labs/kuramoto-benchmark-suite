"""
kuramoto.analysis

Spectral decomposition, Fourier analysis, and visualization tools
for Kuramoto simulation data.

Submodules
----------
spectral
    Spectral decomposition, Fourier amplitude convergence/variability,
    and PSD variability.
graphs
    Re-exports from kuramoto.graphs for adjacency building and graph stats.
viz
    Publication-ready plotting utilities.
"""

from __future__ import annotations

from kuramoto.analysis.graphs import build_adjacency, graph_stats
from kuramoto.analysis.spectral import (
    compute_fourier_coefficients,
    compute_psd,
    compute_spectral_decomposition,
    detect_sync_transition,
    harmonic_analysis,
)
from kuramoto.analysis.viz import (
    plot_fourier_convergence,
    plot_fourier_variability,
    plot_network,
    plot_order_parameter,
    plot_psd_convergence,
    plot_psd_variability,
    plot_time_series,
)

__all__: list[str] = [
    # Graphs re-exports
    "build_adjacency",
    "graph_stats",
    # Spectral
    "compute_fourier_coefficients",
    "compute_psd",
    "compute_spectral_decomposition",
    "detect_sync_transition",
    "harmonic_analysis",
    # Visualization
    "plot_time_series",
    "plot_order_parameter",
    "plot_network",
    "plot_fourier_convergence",
    "plot_fourier_variability",
    "plot_psd_convergence",
    "plot_psd_variability",
]
