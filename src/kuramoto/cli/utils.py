"""
utils.py

Helper functions and formatting utilities for the Kuramoto CLI.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

import os
from typing import Any, Dict, List
from tabulate import tabulate
import click

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ Constants
# -----------------------------------------------------------------------------------------------------------

DEFAULT_DEMO_PATH = "data/examples/demo_dataset.npz"
PLOT_DIR = "plots"

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Helpers
# -----------------------------------------------------------------------------------------------------------

def ensure_plot_dir() -> None:
    """Ensure the plots directory exists."""
    os.makedirs(PLOT_DIR, exist_ok=True)

def print_table(data: List[Dict[str, Any]] | List[List[Any]], headers: List[str] | str = "keys", title: str | None = None) -> None:
    """
    Print a formatted table to the console.

    Parameters
    ----------
    data : List[Dict[str, Any]] or List[List[Any]]
        The data to display.
    headers : List[str] or "keys", default="keys"
        Table headers.
    title : str, optional
        Optional title to print above the table.
    """
    if title:
        click.secho(f"\n--- {title} ---", fg="cyan", bold=True)
    
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
