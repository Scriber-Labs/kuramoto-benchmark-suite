"""
src/kuramoto/cli/style.py

Semantic CLI output styling following Scriber Core and Eigenscribe 4-layer token standards.
Provides consistent contrast-friendly terminal colors using ANSI 256-color palette for
rich Eigenscribe brand theming (blues, purples, pinks, greens, oranges).

Supports automatic fallback to 16-color mode when 256-color terminal detection fails.

Author: Eigenscribe
Date: October 2026
"""

from __future__ import annotations

import os
import sys
from typing import Final

# Force UTF-8 stdout on Windows to support emoji and Unicode box-drawing chars
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
elif sys.platform == "win32":
    # Fallback for older Python: wrap stdout
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import click

__all__: list[str] = [
    # Core messaging
    "cli_message",
    "cli_echo",
    "cli_rule",
    "cli_banner",
    # Semantic levels
    "cli_info",
    "cli_network",
    "cli_quantum",
    "cli_rotor",
    "cli_success",
    "cli_warning",
    "cli_error",
    "cli_highlight",
    # Color palette access
    "EIGENSCRIBE_PALETTE",
    "ansi_256",
    "supports_256_color",
]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 Definitions, Constants & Types — Eigenscribe 256-Color Palette
# -----------------------------------------------------------------------------------------------------------

# Eigenscribe brand palette mapped to ANSI 256-color indices
# Blues (primary), Purples (secondary), Pinks (accents), Greens (success), Oranges (warnings)
EIGENSCRIBE_PALETTE: Final[dict[str, int]] = {
    # --- Blues (Primary domain) ---
    "eigen_blue_dark": 25,       # Deep navy blue
    "eigen_blue": 27,            # Core Eigenscribe blue
    "eigen_blue_bright": 33,     # Bright electric blue
    "eigen_cyan": 51,            # Electric cyan for info
    "eigen_cyan_light": 81,      # Light cyan accent

    # --- Purples (Secondary domain) ---
    "eigen_purple_dark": 55,     # Deep violet
    "eigen_purple": 129,         # Core Eigenscribe purple
    "eigen_purple_bright": 141,  # Bright magenta-purple
    "eigen_magenta": 163,        # Magenta for highlights

    # --- Pinks (Accent domain) ---
    "eigen_pink": 212,           # Soft pink accent
    "eigen_pink_bright": 199,    # Bright pink for emphasis

    # --- Greens (Success domain) ---
    "eigen_green_dark": 22,      # Deep forest green
    "eigen_green": 35,           # Core green
    "eigen_green_bright": 41,    # Bright success green
    "eigen_mint": 121,           # Mint green accent

    # --- Oranges/Ambers (Warning domain) ---
    "eigen_amber": 214,          # Amber warning
    "eigen_orange": 208,         # Core orange
    "eigen_orange_bright": 202,  # Bright orange accent

    # --- Reds (Error domain) ---
    "eigen_red": 160,            # Soft red for errors
    "eigen_red_bright": 196,     # Bright red for critical errors

    # --- Neutrals ---
    "eigen_white": 189,          # Soft white
    "eigen_gray": 145,           # Medium gray
    "eigen_gray_dark": 102,      # Dark gray for dimmed text
}

# Semantic style map: maps message levels to palette keys
STYLE_MAP: Final[dict[str, str]] = {
    "info": "eigen_cyan",
    "network": "eigen_purple_bright",
    "quantum": "eigen_cyan",
    "rotor": "eigen_purple",
    "success": "eigen_green_bright",
    "warning": "eigen_amber",
    "error": "eigen_red_bright",
    "highlight": "eigen_pink_bright",
    "banner_title": "eigen_blue_bright",
    "banner_sub": "eigen_purple",
    "banner_accent": "eigen_cyan_light",
    "rule": "eigen_blue",
}


def supports_256_color() -> bool:
    """
    Detect whether the current terminal supports 256-color output.

    Returns
    -------
    bool
        True if the terminal appears to support 256 colors (COLORTERM contains
        '256color' or we are on Windows with VT100 support enabled).
    """
    colorterm = os.environ.get("COLORTERM", "")
    if "256color" in colorterm:
        return True

    # Windows 10+ with modern terminals (Windows Terminal, Conhost with VT)
    if sys.platform == "win32":
        return True

    # Fallback: check TERM env var
    term = os.environ.get("TERM", "")
    return "256color" in term


def ansi_256(color_name: str, text: str, bold: bool = False) -> str:
    """
    Wrap text with ANSI 256-color escape codes using the Eigenscribe palette.

    Parameters
    ----------
    color_name : str
        Key from EIGENSCRIBE_PALETTE (e.g., "eigen_blue", "eigen_purple").
    text : str
        The text to colorize.
    bold : bool, default=False
        Whether to apply bold weight.

    Returns
    -------
    str
        The ANSI-escaped string ready for terminal output.
    """
    color_index = EIGENSCRIBE_PALETTE.get(color_name)
    if color_index is None:
        return text

    bold_code = "1;" if bold else ""
    return f"\033[{bold_code}38;5;{color_index}m{text}\033[0m"


def _ansi_256_raw(fg_index: int, text: str, bold: bool = False) -> str:
    """
    Apply a raw 256-color index directly (for dynamic color generation).

    Parameters
    ----------
    fg_index : int
        ANSI 256-color index (0-255).
    text : str
        The text to colorize.
    bold : bool, default=False
        Whether to apply bold weight.

    Returns
    -------
    str
        The ANSI-escaped string.
    """
    bold_code = "1;" if bold else ""
    return f"\033[{bold_code}38;5;{fg_index}m{text}\033[0m"


# Fallback 16-color map for terminals that don't support 256 colors
_FALLBACK_16: Final[dict[str, str]] = {
    "info": "bright_cyan",
    "network": "bright_magenta",
    "quantum": "bright_cyan",
    "rotor": "bright_magenta",
    "success": "bright_green",
    "warning": "bright_yellow",
    "error": "bright_red",
    "highlight": "bright_magenta",
    "banner_title": "bright_blue",
    "banner_sub": "bright_magenta",
    "banner_accent": "cyan",
    "rule": "bright_blue",
}


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API — Core Messaging
# -----------------------------------------------------------------------------------------------------------


def cli_message(msg: str, level: str = "info", bold: bool = False) -> None:
    """
    Print a styled message using the Eigenscribe semantic color palette.

    Automatically detects 256-color support and falls back to 16-color mode
    when the terminal does not support extended colors.

    Parameters
    ----------
    msg : str
        Message content to display.
    level : str, default="info"
        Semantic level key from STYLE_MAP.
    bold : bool, default=False
        Whether to format the text in bold weight.
    """
    if supports_256_color():
        color_key = STYLE_MAP.get(level, "eigen_cyan")
        styled = ansi_256(color_key, msg, bold=bold)
        click.echo(styled, color=True)
    else:
        fg = _FALLBACK_16.get(level, "bright_cyan")
        click.secho(msg, fg=fg, bold=bold)


def cli_echo(
    msg: str,
    color: str | None = None,
    bold: bool = False,
    level: str | None = None,
) -> None:
    """
    Print arbitrary text with a specific Eigenscribe palette color.

    Parameters
    ----------
    msg : str
        Message content to display.
    color : str, optional
        Direct palette key (e.g., "eigen_blue", "eigen_pink").
        If provided, takes precedence over `level`.
    bold : bool, default=False
        Whether to apply bold weight.
    level : str, optional
        Fallback semantic level if `color` is not provided.
    """
    if color is not None:
        if supports_256_color():
            styled = ansi_256(color, msg, bold=bold)
            click.echo(styled, color=True)
        else:
            click.secho(msg, bold=bold)
    elif level is not None:
        cli_message(msg, level=level, bold=bold)
    else:
        click.echo(msg, color=True)


def cli_rule(char: str = "-", width: int = 60, level: str = "rule") -> None:
    """
    Print a horizontal rule line with semantic coloring.

    Parameters
    ----------
    char : str, default="-"
        Character to repeat for the rule line (use ASCII-safe chars for Windows compat).
    width : int, default=60
        Number of characters wide.
    level : str, default="rule"
        Semantic color level.
    """
    line = char * width
    cli_message(line, level=level)


def cli_banner(title: str, subtitle: str | None = None) -> None:
    """
    Print a styled banner header with Eigenscribe brand colors.

    Parameters
    ----------
    title : str
        Main banner title.
    subtitle : str, optional
        Optional secondary subtitle line.
    """
    cli_echo("", color="eigen_blue_bright", bold=True)
    cli_echo(title, color="eigen_blue_bright", bold=True)

    if subtitle:
        cli_echo(subtitle, color="eigen_purple", bold=False)

    cli_rule(level="rule")
    cli_echo("")


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API — Semantic Message Functions
# -----------------------------------------------------------------------------------------------------------


def cli_info(msg: str) -> None:
    """
    Print an informational prompt (Electric Cyan).

    Parameters
    ----------
    msg : str
        Informational message string.
    """
    cli_message(f"ℹ️  {msg}", level="info")


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
    cli_message(f"⚛️  {msg}", level="quantum", bold=True)


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
    cli_message(f"⚠️  {msg}", level="warning")


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
    Print an emphasized highlight message (Bright Pink).

    Parameters
    ----------
    msg : str
        Highlight message string.
    """
    cli_message(f"✨ {msg}", level="highlight", bold=True)


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for CLI style functions and 256-color palette."""
    click.echo("", color=True)
    cli_banner("EIGENSCRIBE CLI STYLE TEST", "256-Color Palette Verification")

    # Semantic messages
    cli_info("Info message — Electric Cyan")
    cli_network("Network message — Bright Purple")
    cli_quantum("Quantum message — Electric Cyan")
    cli_rotor("Rotor message — Core Purple")
    cli_success("Success message — Bright Green")
    cli_warning("Warning message — Amber")
    cli_error("Error message — Bright Red")
    cli_highlight("Highlight message — Bright Pink")

    # Palette showcase
    cli_rule()
    cli_echo("🎨 Eigenscribe 256-Color Palette Showcase:", color="eigen_white", bold=True)
    cli_rule()

    # Compact palette display
    if supports_256_color():
        groups = {
            "🔵 Blues": ["eigen_blue_dark", "eigen_blue", "eigen_blue_bright", "eigen_cyan", "eigen_cyan_light"],
            "🟣 Purples": ["eigen_purple_dark", "eigen_purple", "eigen_purple_bright", "eigen_magenta"],
            "🩷 Pinks": ["eigen_pink", "eigen_pink_bright"],
            "🟢 Greens": ["eigen_green_dark", "eigen_green", "eigen_green_bright", "eigen_mint"],
            "🟠 Oranges": ["eigen_amber", "eigen_orange", "eigen_orange_bright"],
            "🔴 Reds": ["eigen_red", "eigen_red_bright"],
            "⚪ Neutrals": ["eigen_white", "eigen_gray", "eigen_gray_dark"],
        }
        for label, colors in groups.items():
            parts = [ansi_256(c, c) for c in colors]
            click.echo(f"  {label}: {' '.join(parts)}", color=True)
    else:
        click.echo("  (256-color mode not available — using 16-color fallback)", color=True)

    cli_rule()
    cli_success("Style smoke test passed.")
    click.echo("", color=True)


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point for standalone execution."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
