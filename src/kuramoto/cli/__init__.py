"""
src/kuramoto/cli

Command line interface (CLI) for the Kuramoto Benchmark Suite.
Supports running and benchmarking classical ODE, GA rotor, and quantum SCF solvers.
Features Eigenscribe 256-color terminal theming with automatic fallback.

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
    EIGENSCRIBE_PALETTE,
    ansi_256,
    cli_banner,
    cli_echo,
    cli_error,
    cli_highlight,
    cli_info,
    cli_message,
    cli_network,
    cli_quantum,
    cli_rotor,
    cli_rule,
    cli_success,
    cli_warning,
    supports_256_color,
)
from .utils import DEFAULT_DEMO_PATH, PLOT_DIR, ensure_plot_dir, print_table

__all__: list[str] = [
    # CLI entry
    "cli",
    "main",
    # Commands
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
    # Style — semantic messages
    "cli_info",
    "cli_network",
    "cli_quantum",
    "cli_rotor",
    "cli_success",
    "cli_warning",
    "cli_error",
    "cli_highlight",
    # Style — core messaging
    "cli_message",
    "cli_echo",
    "cli_rule",
    "cli_banner",
    # Style — palette access
    "EIGENSCRIBE_PALETTE",
    "ansi_256",
    "supports_256_color",
    # Utils
    "DEFAULT_DEMO_PATH",
    "PLOT_DIR",
    "ensure_plot_dir",
    "print_table",
]
