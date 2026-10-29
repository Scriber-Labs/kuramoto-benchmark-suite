"""
src/kuramoto/cli/style.py

Semantic CLI output styling following Scriber Core and Eigenscribe 4-layer token standards.
Provides consistent contrast-friendly terminal colors for attention support, focal
prompts, network topology cues, quantum execution cues, and invariant verifications.

Author: Eigenscribe
Date: October 2026
"""

from __future__ import annotations

from typing import Final

import click

__all__: list[str] = [
    "cli_message",
    "cli_info",
    "cli_network",
    "cli_quantum",
    "cli_rotor",
    "cli_zbw",
    "cli_success",
    "cli_warning",
    "cli_error",
    "cli_highlight",
    "cli_section",
    "cli_divider",
]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------

STYLE_MAP: Final[dict[str, str]] = {
    "info": "bright_cyan",
    "network": "bright_magenta",
    "quantum": "bright_cyan",
    "rotor": "bright_magenta",
    "zbw": "bright_yellow",
    "success": "bright_green",
    "warning": "bright_yellow",
    "error": "bright_red",
    "highlight": "bright_magenta",
    "section": "white",
}

# Extended color palette for richer output
COLOR_PALETTE: Final[dict[str, str]] = {
    "cyan": "cyan",
    "magenta": "magenta",
    "green": "green",
    "yellow": "yellow",
    "red": "red",
    "blue": "blue",
    "white": "white",
    "bright_cyan": "bright_cyan",
    "bright_magenta": "bright_magenta",
    "bright_green": "bright_green",
    "bright_yellow": "bright_yellow",
    "bright_red": "bright_red",
    "bright_blue": "bright_blue",
    "bright_white": "bright_white",
}


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


def cli_section(title: str) -> None:
    """
    Print a section header with decorative borders.

    Parameters
    ----------
    title : str
        Section title to display.
    """
    border = "─" * 50
    click.echo("")
    click.secho(f" {border}", fg="bright_white", bold=True)
    click.secho(f"  {title}", fg="bright_white", bold=True)
    click.secho(f" {border}", fg="bright_white", bold=True)


def cli_divider() -> None:
    """
    Print a simple horizontal divider line.
    """
    click.secho(" ─" * 25, fg="bright_white")


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for CLI style functions."""
    print("💨 Running style smoke test...")
    cli_info("Test info message")
    cli_network("Test network message")
    cli_quantum("Test quantum message")
    cli_rotor("Test rotor message")
    cli_zbw("Test ZBW message")
    cli_success("Test success message")
    cli_warning("Test warning message")
    cli_error("Test error message")
    cli_highlight("Test highlight message")
    cli_section("Test Section Header")
    cli_divider()
    print("✅ Style smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point for standalone execution."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
