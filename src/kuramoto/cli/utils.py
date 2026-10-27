"""
utils.py

Helper functions and formatting utilities for the Kuramoto CLI.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

import os
from typing import Any, Final

import click
from tabulate import tabulate

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
        click.secho(f"\n--- {title} ---", fg="bright_cyan", bold=True)

    table = tabulate(data, headers=headers, tablefmt="rounded_grid")
    click.echo(table)
    click.echo("")


def print_header() -> None:
    """Print the Kuramoto Benchmark Suite header."""
    header = """
  ---------------   KURAMOTO BENCHMARK SUITE   --------------------

  You are now using the Command line interface of Kuramoto, a tool for
  simulating and analyzing oscillator networks, created as a
  benchmark-grade suite.

  This is a python package currently installed in your python environment.
    """
    click.secho(header, fg="bright_blue", bold=True)


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
