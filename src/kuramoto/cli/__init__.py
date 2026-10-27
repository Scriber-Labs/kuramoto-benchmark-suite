"""
src/kuramoto/cli

Command line interface (CLI) for the Kuramoto Benchmark Suite.
Supports running and benchmarking classical ODE, GA rotor, and quantum SCF solvers.

Author: Eigenscribe
Date: October 2026
"""

from __future__ import annotations

from .commands import (
    benchmark,
    datasetforbeginners,
    distributions,
    fourierconvergence,
    fouriervariability,
    generate,
    network,
    psdconvergence,
    psdvariability,
    qasm,
    quantum,
    time,
)
from .main import cli, main
from .style import (
    cli_error,
    cli_info,
    cli_network,
    cli_quantum,
    cli_rotor,
    cli_success,
    cli_warning,
)
from .utils import DEFAULT_DEMO_PATH, PLOT_DIR, ensure_plot_dir, print_table

__all__: list[str] = [
    "cli",
    "main",
    "datasetforbeginners",
    "generate",
    "quantum",
    "qasm",
    "benchmark",
    "time",
    "fouriervariability",
    "fourierconvergence",
    "psdvariability",
    "psdconvergence",
    "network",
    "distributions",
    "cli_info",
    "cli_network",
    "cli_quantum",
    "cli_rotor",
    "cli_success",
    "cli_warning",
    "cli_error",
    "DEFAULT_DEMO_PATH",
    "PLOT_DIR",
    "ensure_plot_dir",
    "print_table",
]
