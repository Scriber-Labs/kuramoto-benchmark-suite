"""
main.py

Main entry point for the Kuramoto CLI.

Author: Eigenscribe
Date: May 2026
"""

from __future__ import annotations

import click
from .utils import print_header
from .commands import (
    datasetforbeginners,
    generate,
    time,
    fouriervariability,
    fourierconvergence,
    psdvariability,
    psdconvergence,
    network,
    distributions
)

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    ---------------   KURAMOTO   --------------------

    A tool for simulating and analyzing Kuramoto oscillator networks.
    Inspired by 'satis' for spectral analysis.
    """
    if ctx.invoked_subcommand is None:
        print_header()
        click.echo(ctx.get_help())

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ Command Registration
# -----------------------------------------------------------------------------------------------------------

cli.add_command(datasetforbeginners)
cli.add_command(generate)
cli.add_command(time)
cli.add_command(fouriervariability)
cli.add_command(fourierconvergence)
cli.add_command(psdvariability)
cli.add_command(psdconvergence)
cli.add_command(network)
cli.add_command(distributions)

def main() -> None:
    """Entry point for the kuramoto script."""
    cli()

if __name__ == "__main__":
    main()
