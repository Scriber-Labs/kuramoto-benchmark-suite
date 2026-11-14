# src/kuramoto/cli/style.py
"""
style.py

Semantic CLI output styling following Scriber Core and Eigenscribe 4-layer token standards.
Provides consistent contrast-friendly terminal colors for attention support, focal
prompts, network topology cues, quantum execution cues, and invariant verifications.

Author: Eigenscribe
Date: October 2026
"""

from __future__ import annotations

import os
import re
from collections.abc import Sequence
from typing import Final, TypeAlias

import click
import sys

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

__all__: list[str] = [
    # Gradients & Colors
    "multi_gradient",
    "cli_gradient",
    "PRESETS",
    "RGB",
    "Color",
    "hex_to_rgb",
    # Domain color helpers
    "style_coprime_term",
    "style_coprime_gcd",
    "style_coprime_coeff",
    # Semantic messaging
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
    "cli_section",
    "cli_divider",
    "cli_echo",
    "cli_rule",
    "cli_banner",
    "EIGENSCRIBE_PALETTE",
    "ansi_256",
    "supports_256_color",
]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------

RGB: TypeAlias = tuple[int, int, int]
Color: TypeAlias = str | RGB

PRESETS: Final[dict[str, tuple[str, ...]]] = {
    # 🐉 Signature Eigenscribe (without pink): Blue (#0a95eb) -> Periwinkle (#5280ff) -> Purple (#a855f7)
    "eigenscribe-1": ("#38bdf8", "#0A95EB", "#5280ff", "#5e17eb"),
    # 🌟 Signature Eigenscribe (with pink): Blue (#00a6ff) -> Purple (#a855f7) -> Magenta (#ff00c3)
    "eigenscribe-2": ("#00a6ff", "#a855f7", "#ff00c3"),
    "electric": ("#00a6ff", "#a855f7", "#ff00c3"),
    # 🌅 Solar Sunset: Orange (#ff6b35) -> Amber (#f7c548) -> Crimson (#d7263d)
    "sunset": ("#ff6b35", "#f7c548", "#ff40a1"),
    # 🌲 Deep Forest: Olive (#a7c957) -> Teal (#2a9d8f) -> Pine (#264653)
    "forest": ("#a7c957", "#2a9d8f", "#264653"),
    # 🌌 Midnight Cosmic: Sky Cyan (#38bdf8) -> Lavender (#818cf8) -> Rose (#f43f5e)
    "midnight": ("#38bdf8", "#818cf8", "#f43f5e"),
    # 🌿 Quantum Aurora: Aqua (#06b6d4) -> Emerald (#10b981) -> Lime (#84cc16)
    "aurora": ("#06b6d4", "#10b981", "#84cc16"),
    # ⚡ Cyberpunk Neon: Electric Cyan (#00f0ff) -> Deep Violet (#7000ff) -> Hot Pink (#ff007b)
    "cyberpunk": ("#00f0ff", "#7000ff", "#ff007b"),
    # 💜 Purple Gradient: Purple-1 (#7952f5) -> Warm purple (#a855f7)
    "purple_gradient": ("#7952f5", "#a855f7")
}

STYLE_MAP: Final[dict[str, str]] = {
    "info": "bright_cyan",
    "network": "bright_magenta",
    "quantum": "bright_cyan",
    "rotor": "bright_magenta",
    "zbw": "bright_yellow",
    "coprime": "bright_cyan",
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

# 256-color ANSI palette for terminals that support extended color
ANSI_256_PALETTE: Final[dict[str, int]] = {
    "eigen_cyan": 81,
    "eigen_cyan_light": 122,
    "eigen_magenta": 135,
    "eigen_green": 41,
    "eigen_yellow": 178,
    "eigen_red": 196,
    "eigen_blue": 69,
    "eigen_blue_bright": 75,
    "eigen_purple": 141,
    "eigen_white": 189,
}

# Canonical alias exposed as EIGENSCRIBE_PALETTE for external consumers
EIGENSCRIBE_PALETTE: Final[dict[str, int]] = ANSI_256_PALETTE


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
        Color key from ``ANSI_256_PALETTE`` (e.g. "eigen_cyan").
    text : str
        Text to colorize.
    bold : bool, default=False
        Whether to apply bold weight.

    Returns
    -------
    str
        ANSI-escaped string ready for ``click.echo(..., color=True)``.
    """
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
        Hex color string (e.g. '#00a6ff' or '00a6ff').

    Returns
    -------
    RGB
        Tuple of three integer color channels (0 to 255).

    Raises
    ------
    ValueError
        If hex_color is not a valid 6-digit hexadecimal color string.
    """
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


def multi_gradient(
    text: str,
    colors: Sequence[Color] = PRESETS["eigenscribe-2"],
    *,
    bold: bool = True,
) -> str:
    """
    Return text formatted with an ANSI TrueColor gradient across multiple color stops.

    Parameters
    ----------
    text : str
        The input text to colorize.
    colors : Sequence[Color], default=PRESETS["eigenscribe-2"]
        A sequence of at least two color stops (hex strings or RGB tuples).
    bold : bool, default=True
        Whether to apply bold ANSI formatting.

    Returns
    -------
    str
        ANSI TrueColor-escaped string with color resets.
    """
    if not text:
        return ""

    if len(colors) < 2:
        raise ValueError("Provide at least two colors for a gradient")

    rgb_colors = [_normalize_color(color) for color in colors]
    style = "1;" if bold else ""
    segments = len(rgb_colors) - 1
    output: list[str] = []

    for index, character in enumerate(text):
        position = index / (len(text) - 1) if len(text) > 1 else 0.0
        scaled_position = position * segments
        segment = min(int(scaled_position), segments - 1)
        segment_position = scaled_position - segment

        start = rgb_colors[segment]
        end = rgb_colors[segment + 1]

        red = round(start[0] + segment_position * (end[0] - start[0]))
        green = round(start[1] + segment_position * (end[1] - start[1]))
        blue = round(start[2] + segment_position * (end[2] - start[2]))

        output.append(f"\033[{style}38;2;{red};{green};{blue}m{character}")

    output.append("\033[0m")
    return "".join(output)


# Canonical alias
cli_gradient = multi_gradient


def style_coprime_term(val: int | str) -> str:
    """Color (a, b) coprime terms in cyan (#00a6ff)."""
    return f"\033[38;2;0;166;255m{val}\033[0m"


def style_coprime_gcd(val: int | str) -> str:
    """Color gcd values in green (#28d728)."""
    return f"\033[38;2;40;215;40m{val}\033[0m"


def style_coprime_coeff(val: int | str) -> str:
    """Color Bezout coefficients (x, y) in magenta (#ff00c3)."""
    return f"\033[38;2;255;0;195m{val}\033[0m"


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


def cli_coprime(msg: str) -> None:
    """
    Print a coprime sampling / CRT reconstruction update (Number Theory).

    Parameters
    ----------
    msg : str
        Coprime / number theory message string.
    """
    cli_message(f"🔢 {msg}", level="coprime", bold=True)


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
    cli_coprime("Test coprime message")
    cli_success("Test success message")
    cli_warning("Test warning message")
    cli_error("Test error message")
    cli_highlight("Test highlight message")
    cli_section("Test Section Header")
    cli_divider()

    # Test TrueColor gradient engine
    assert hex_to_rgb("#00a6ff") == (0, 166, 255)
    grad = multi_gradient("Test Gradient", PRESETS["electric"])
    assert "\033[0m" in grad
    assert cli_gradient("Alias Test") != ""

    # Test coprime domain formatters
    term = style_coprime_term(7)
    gcd_str = style_coprime_gcd(1)
    coeff = style_coprime_coeff(-3)
    assert "7" in term and "1" in gcd_str and "-3" in coeff

    print("✅ Style smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point for standalone execution."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
