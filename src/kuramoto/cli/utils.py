# src/kuramoto/cli/utils.py
"""
utils.py

Helper functions and formatting utilities for the Kuramoto CLI.
Provides table formatting, directory management, and styled header output
using the Eigenscribe 256-color palette from scriber_core.

Author: Eigenscribe
Date: May 2026
Last Updated: November 2026
"""

from __future__ import annotations

import os
from typing import Any, Final

import click
from tabulate import tabulate

from eigenscribe.cli.branding import print_brand_header
from eigenscribe.cli.messaging import ansi_256, cli_rule, supports_256_color

__all__: list[str] = [
    "DEFAULT_DEMO_PATH",
    "PLOT_DIR",
    "ensure_plot_dir",
    "print_table",
    "print_header",
]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------

DEFAULT_DEMO_PATH: Final[str] = "data/examples/demo_dataset.npz"
PLOT_DIR: Final[str] = "plots"

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API / Helpers
# -----------------------------------------------------------------------------------------------------------


def ensure_plot_dir() -> None:
    """Ensure the plots directory exists."""
    os.makedirs(PLOT_DIR, exist_ok=True)


def print_table(
    data: list[dict[str, Any]] | list[list[Any]],
    headers: list[str] | str = "keys",
    title: str | None = None,
) -> None:
    """
    Print a formatted table to the console using rounded grid borders.

    Parameters
    ----------
    data : list[dict[str, Any]] or list[list[Any]]
        The tabular records or matrix to display.
    headers : list[str] or "keys", default="keys"
        Table headers.
    title : str, optional
        Optional header title to print above the table.
    """
    if title:
        if supports_256_color():
            click.echo("", color=True)
            click.echo(ansi_256("eigen_cyan", f"-- {title} --", bold=True), color=True)
        else:
            click.secho(f"\n--- {title} ---", fg="bright_cyan", bold=True)

    table = tabulate(data, headers=headers, tablefmt="rounded_grid")
    click.echo(table, color=True)
    click.echo("", color=True)


def print_header() -> None:
    """Print the Kuramoto Benchmark Suite header with Eigenscribe brand colors."""
    print_brand_header(
        title="🔱 KURAMOTO BENCHMARK SUITE — OSCILLATOR NETWORK SIMULATION",
        description="Supports classical ODE, Geometric Algebra (GA) rotor, and hybrid Quantum SCF solvers.",
        width=56,
    )
    cli_rule(char="·", width=56, level="rule")


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for CLI utils."""
    print("💨 Running utils smoke test...")
    ensure_plot_dir()
    assert os.path.exists(PLOT_DIR)
    print_table([{"Key": "Value", "Status": "OK"}], title="Smoke Test Table")
    print("✅ Utils smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point for standalone execution."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
