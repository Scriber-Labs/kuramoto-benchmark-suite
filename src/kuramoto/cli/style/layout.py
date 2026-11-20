"""
layout.py

Structural formatting — section headers, dividers, rules, and banners.

Author: Eigenscribe
Date: November 20, 2026
"""

from __future__ import annotations

import click

from kuramoto.cli.style.palettes import STYLE_MAP
from kuramoto.cli.style.color_utils import supports_256_color, ansi_256, hex_to_rgb

__all__: list[str] = [
    "cli_echo",
    "cli_rule",
    "cli_banner",
    "cli_section",
    "cli_divider",
]


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API
# -----------------------------------------------------------------------------------------------------------


def cli_echo(msg: str, **kwargs: str) -> None:
    """
    Print a message using click.echo with color enabled.

    Parameters
    ----------
    msg : str
        Message content to display.
    **kwargs
        Additional keyword arguments passed to ``click.echo``.
    """
    kwargs.setdefault("color", True)
    click.echo(msg, **kwargs)


def cli_rule(char: str = "─", width: int = 56, level: str = "info") -> None:
    """
    Print a horizontal rule line with a given character and style.

    Parameters
    ----------
    char : str, default="─"
        Character used to draw the rule.
    width : int, default=56
        Number of characters in the rule.
    level : str, default="info"
        Semantic level for color lookup in ``STYLE_MAP``.
    """
    fg = STYLE_MAP.get(level, "bright_cyan")
    # Handle hex colors from scriber_core palette
    if fg.startswith("#"):
        rgb = hex_to_rgb(fg)
        click.echo(f"\033[1;38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{char * width}\033[0m")
    else:
        click.secho(char * width, fg=fg)


def cli_banner() -> None:
    """
    Print the Kuramoto Benchmark Suite branded banner with 256-color support.
    Falls back to standard click colors when 256-color is unavailable.
    """
    click.echo("")
    if supports_256_color():
        click.echo(
            ansi_256("eigen_blue_bright", "  " + "=" * 56, bold=True), color=True
        )
        click.echo(
            ansi_256("eigen_blue_bright", "     KURAMOTO BENCHMARK SUITE", bold=True),
            color=True,
        )
        click.echo(
            ansi_256(
                "eigen_purple",
                "     Oscillator Network Simulation & Analysis Framework",
                bold=False,
            ),
            color=True,
        )
        click.echo(
            ansi_256("eigen_blue_bright", "  " + "=" * 56, bold=True), color=True
        )
    else:
        click.secho("  " + "=" * 56, fg="bright_blue", bold=True)
        click.secho("     KURAMOTO BENCHMARK SUITE", fg="bright_blue", bold=True)
        click.secho(
            "     Oscillator Network Simulation & Analysis Framework",
            fg="bright_magenta",
        )
        click.secho("  " + "=" * 56, fg="bright_blue", bold=True)
    click.echo("")


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
# 💨 Smoke Tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for layout functions."""
    print("💨 Running layout.py smoke tests...")
    
    # Test that functions run without error
    cli_echo("Test echo")
    cli_rule()
    cli_section("Test Section")
    cli_divider()
    
    print("✅ layout.py smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry Point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Run smoke tests for the layout module."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
