"""
main.py

Main entry point for the Kuramoto CLI.

Author: Eigenscribe
Date: May 2026
Last Updated: October 2026
"""

from __future__ import annotations

import click

from .commands import (
    benchmark,
    dash_export,
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
from .utils import print_header

__all__: list[str] = ["cli", "main"]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 CLI Group Definition
# -----------------------------------------------------------------------------------------------------------


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    ---------------   KURAMOTO BENCHMARK SUITE   --------------------

    A comprehensive framework for simulating, analyzing, and benchmarking
    classical ODE, Geometric Algebra (GA) rotor, and hybrid Quantum SCF
    Kuramoto oscillator networks.
    """
    if ctx.invoked_subcommand is None:
        print_header()
        click.echo(ctx.get_help())


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Command Registration
# -----------------------------------------------------------------------------------------------------------

cli.add_command(datasetforbeginners)
cli.add_command(dash_export)
cli.add_command(generate)
cli.add_command(quantum)
cli.add_command(qasm)
cli.add_command(benchmark)
cli.add_command(time)
cli.add_command(fouriervariability)
cli.add_command(fourierconvergence)
cli.add_command(psdvariability)
cli.add_command(psdconvergence)
cli.add_command(network)
cli.add_command(distributions)


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for CLI group registration."""
    print("💨 Running main CLI smoke test...")
    commands = list(cli.commands.keys())
    expected = [
        "datasetforbeginners",
        "dash-export",
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
    ]
    for cmd in expected:
        assert cmd in commands, f"Command '{cmd}' missing from CLI group."
    print("✅ Main CLI smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point for the kuramoto script."""
    cli()


if __name__ == "__main__":
    main()
