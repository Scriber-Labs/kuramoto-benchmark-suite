"""
messages.py

Semantic echo functions — domain-specific CLI messages with emojis.

Author: Eigenscribe
Date: November 20, 2026
"""

from __future__ import annotations

import click

from kuramoto.cli.style.color_utils import hex_to_rgb
from kuramoto.cli.style.palettes import STYLE_MAP

__all__: list[str] = [
    "cli_message",
    "cli_info",
    "cli_network",
    "cli_quantum",
    "cli_rotor",
    "cli_zbw",
    "cli_coprime",
    "cli_success",
    "cli_warning",
    "cli_error",
    "cli_highlight",
]


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API
# -----------------------------------------------------------------------------------------------------------


def cli_message(msg: str, level: str = "info", bold: bool = False) -> None:
    """
    Print a styled message using the semantic color palette.

    Parameters
    ----------
    msg : str
        Message content to display.
    level : str, default="info"
        Semantic level ("info", "network", "quantum", "rotor", "success", "warning", "error", "highlight").
    bold : bool, default=False
        Whether to format the text in bold weight.
    """
    fg = STYLE_MAP.get(level, "bright_cyan")
    # Handle hex colors from scriber_core palette
    if fg.startswith("#"):
        rgb = hex_to_rgb(fg)
        style = "1;" if bold else ""
        click.echo(f"\033[{style}38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{msg}\033[0m")
    else:
        click.secho(msg, fg=fg, bold=bold)


def cli_info(msg: str) -> None:
    """
    Print an informational prompt (Electric Cyan).

    Parameters
    ----------
    msg : str
        Informational message string.
    """
    cli_message(f"ℹ️ {msg}", level="info")


def cli_network(msg: str) -> None:
    """
    Print a topology or structural network update (Secondary Violet).

    Parameters
    ----------
    msg : str
        Topology/network message string.
    """
    cli_message(f"🌐 {msg}", level="network", bold=True)


def cli_quantum(msg: str) -> None:
    """
    Print a quantum SCF solver update (Electric Cyan / Qubit).

    Parameters
    ----------
    msg : str
        Quantum execution update message string.
    """
    cli_message(f"⚛️ {msg}", level="quantum", bold=True)


def cli_rotor(msg: str) -> None:
    """
    Print a Clifford GA rotor solver update (Geometric Algebra).

    Parameters
    ----------
    msg : str
        Geometric Algebra rotor solver message string.
    """
    cli_message(f"🌀 {msg}", level="rotor", bold=True)


def cli_success(msg: str) -> None:
    """
    Print a success confirmation (Tertiary Green).

    Parameters
    ----------
    msg : str
        Success message string.
    """
    cli_message(f"✅ {msg}", level="success", bold=True)


def cli_warning(msg: str) -> None:
    """
    Print a warning notification (Quaternary Amber).

    Parameters
    ----------
    msg : str
        Warning message string.
    """
    cli_message(f"⚠️ {msg}", level="warning")


def cli_error(msg: str) -> None:
    """
    Print an error alert (Pernary Red/Magenta).

    Parameters
    ----------
    msg : str
        Error message string.
    """
    cli_message(f"❌ {msg}", level="error", bold=True)


def cli_highlight(msg: str) -> None:
    """
    Print an emphasized highlight message.

    Parameters
    ----------
    msg : str
        Highlight message string.
    """
    cli_message(f"✨ {msg}", level="highlight", bold=True)


def cli_zbw(msg: str) -> None:
    """
    Print a ZBW (golden-ratio ensemble) model update.

    Parameters
    ----------
    msg : str
        ZBW model message string.
    """
    cli_message(f"🌟 {msg}", level="zbw", bold=True)


def cli_coprime(msg: str) -> None:
    """
    Print a coprime sampling / CRT reconstruction update (Number Theory).

    Parameters
    ----------
    msg : str
        Coprime / number theory message string.
    """
    cli_message(f"🔢 {msg}", level="coprime", bold=True)


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke Tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for message functions."""
    print("💨 Running messages.py smoke tests...")

    # Test that all message functions run without error
    cli_info("Test info message")
    cli_network("Test network message")
    cli_quantum("Test quantum message")
    cli_rotor("Test rotor message")
    cli_zbw("Test ZBW message")
    cli_coprime("Test coprime message")
    cli_success("Test success message")
    cli_warning("Test warning message")
    cli_error("Test error message")
    cli_highlight("Test highlight message")

    print("✅ messages.py smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry Point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Run smoke tests for the messages module."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
