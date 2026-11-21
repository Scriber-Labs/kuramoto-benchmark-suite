# src/kuramoto/cli/style/color_utils.py
"""
color_utils.py

Low-level color conversion and terminal detection utilities.

Author: Eigenscribe
Date: November 20, 2026
"""

from __future__ import annotations

import os
import sys

import click

from kuramoto.cli.style.types import RGB, Color

__all__: list[str] = [
    "supports_256_color",
    "ansi_256",
    "hex_to_rgb",
    "_normalize_color",
    "print_hex_swatches",
]


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API
# -----------------------------------------------------------------------------------------------------------


def supports_256_color() -> bool:
    """
    Check whether the current terminal supports 256-color ANSI output.

    Returns
    -------
    bool
        True if the terminal supports 256 colors, False otherwise.
    """
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return False
    if not bool(getattr(sys.stdout, "isatty", lambda: False)()):
        return False
    if sys.platform == "win32":
        return True
    term = os.environ.get("TERM", "")
    colorterm = os.environ.get("COLORTERM", "")
    return (
        "256color" in term
        or "xterm" in term
        or "truecolor" in colorterm
        or "24bit" in colorterm
    )


def ansi_256(color_name: str, text: str, bold: bool = False) -> str:
    """
    Return a string wrapped in 256-color ANSI escape codes.

    Parameters
    ----------
    color_name : str
        Color key from ``ANSI_256_PALETTE`` (e.g., "eigen_cyan").
    text : str
        Text to colorize.
    bold : bool, default=False
        Whether to apply bold weight.

    Returns
    -------
    str
        ANSI-escaped string ready for ``clickl.echo(..., color=True)``.
    """
    from kuramoto.cli.style.palettes import ANSI_256_PALETTE

    color_code = ANSI_256_PALETTE.get(color_name, 81)
    parts: list[str] = []
    if bold:
        parts.append("1")
    parts.append(f"38;5;{color_code}")
    return f"\033[{';'.join(parts)}m{text}\033[0m"


def hex_to_rgb(hex_color: str) -> RGB:
    """
    Convert a six-digit hex color string, with or without '#', to an (R, G, B) tuple.

    Parameters
    ----------
    hex_color : str
        Hex color string (e.g., '#00a6ff' or '00a6ff').

    Returns
    -------
    RGB
       Tuple of three integer color channels (0 to 255).

    Raises
    ------
    ValueError
        If hex_color is not a valid 6-digit hexadecimal color string.
    """
    import re

    value = hex_color.removeprefix("#")
    if re.fullmatch(r"[0-9a-fA-F]{6}", value) is None:
        raise ValueError(f"Expected a six-digit hex color, got {hex_color!r}")

    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
    )


def _normalize_color(color: Color) -> RGB:
    """Convert a hex string or validate and return an RGB tuple."""
    if isinstance(color, str):
        return hex_to_rgb(color)

    if (
        len(color) != 3
        or any(not isinstance(ch, int) or isinstance(ch, bool) for ch in color)
        or any(not 0 <= ch <= 255 for ch in color)
    ):
        raise ValueError(
            f"RGB colors must contain three integers from 0 to 255: {color!r}"
        )
    return color


def print_hex_swatches(label: str, palette: dict[str, str], width: int = 16) -> None:
    """
    Print colored swatches for a hex color palette.

    Parameters
    ----------
    label : str
        Palette name to display as header.
    palette : dict[str, str]
        Mapping of color names to hex color strings.
    width : int, default=16
        Column width for color names.
    """
    click.echo("")
    click.secho(f" 🎨 {label} Swatches:", fg="bright_white", bold=True, color=True)
    for name, hex_color in palette.items():
        rgb = hex_to_rgb(hex_color)
        click.echo(f"  {name:{width}s} ", nl=False)
        click.echo(
            f"\033[1;38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{'█' * 10}\033[0m", color=True
        )


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke Tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for color utilities."""
    print("👟💨 Running color_utils.py smoke tests...")
    assert hex_to_rgb("#00a6ff") == (0, 166, 255)
    assert hex_to_rgb("00a6ff") == (0, 166, 255)
    assert _normalize_color("#ff6b35") == (255, 107, 53)
    assert _normalize_color((255, 107, 53)) == (255, 107, 53)
    print("✅💨 color_utils.py smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry Point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Ru smoke tests for the color_utils module."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
