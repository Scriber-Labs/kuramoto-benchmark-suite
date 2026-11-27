"""
messages.py

Domain-specific CLI messages with emojis — extends scriber_core messaging
with Kuramoto-specific semantic levels (network, quantum, rotor, ZBW, coprime).

Author: Eigenscribe
Date: November 20, 2026
"""

from __future__ import annotations

__all__: list[str] = [
    "cli_network",
    "cli_quantum",
    "cli_rotor",
    "cli_zbw",
    "cli_coprime",
]


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API — Domain-specific semantic messages
# -----------------------------------------------------------------------------------------------------------


def cli_network(msg: str) -> None:
    """
    Print a topology or structural network update (Secondary Violet).

    Parameters
    ----------
    msg : str
        Topology/network message string.
    """
    from eigenscribe.cli.messaging import ansi_256

    styled = ansi_256("eigen_purple", f"🌐 {msg}", bold=True)
    import click
    click.echo(styled, color=True)


def cli_quantum(msg: str) -> None:
    """
    Print a quantum SCF solver update (Electric Cyan / Qubit).

    Parameters
    ----------
    msg : str
        Quantum execution update message string.
    """
    from eigenscribe.cli.messaging import ansi_256

    styled = ansi_256("eigen_cyan", f"⚛️ {msg}", bold=True)
    import click
    click.echo(styled, color=True)


def cli_rotor(msg: str) -> None:
    """
    Print a Clifford GA rotor solver update (Geometric Algebra).

    Parameters
    ----------
    msg : str
        Geometric Algebra rotor solver message string.
    """
    from eigenscribe.cli.messaging import ansi_256

    styled = ansi_256("eigen_accent_green", f"🌀 {msg}", bold=True)
    import click
    click.echo(styled, color=True)


def cli_zbw(msg: str) -> None:
    """
    Print a ZBW (golden-ratio ensemble) model update.

    Parameters
    ----------
    msg : str
        ZBW model message string.
    """
    from eigenscribe.cli.messaging import ansi_256

    styled = ansi_256("eigen_accent_amber", f"🌟 {msg}", bold=True)
    import click
    click.echo(styled, color=True)


def cli_coprime(msg: str) -> None:
    """
    Print a coprime sampling / CRT reconstruction update (Number Theory).

    Parameters
    ----------
    msg : str
        Coprime / number theory message string.
    """
    from eigenscribe.cli.messaging import ansi_256

    styled = ansi_256("eigen_accent_magenta", f"🔢 {msg}", bold=True)
    import click
    click.echo(styled, color=True)


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke Tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for domain-specific message functions."""
    print("💨 Running messages.py smoke tests...")

    # Test that all domain-specific message functions run without error
    cli_network("Test network message")
    cli_quantum("Test quantum message")
    cli_rotor("Test rotor message")
    cli_zbw("Test ZBW message")
    cli_coprime("Test coprime message")

    print("✅ messages.py smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry Point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Run smoke tests for the messages module."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
