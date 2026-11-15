# frontend/the_scriber_experience/cli/messaging.py
"""
messaging.py

Semantic CLI output styling following Scriber Core and Eigenscribe 4-layer token standards.
(Originally adapted from ../boilerplates/python/cli_style_boilerplate.py)

Provides a ready-to-use Eigenscribe 256-color terminal palette with automatic
fallback to 16-color mode, plus semantic message helpers (info, success, warning,
error, highlight, network, quantum, rotor) and decorative elements (banners, rules, tables).

Inspired by the "EigenBeast" game CLI pattern — uses color-coded semantic levels
to make terminal output visually engaging while remaining accessible and ADHD-friendly.

Usage
-----
>>> from the_scriber_experience.cli.messaging import ansi_256, cli_banner, cli_info, cli_success
>>> cli_banner("MY APP", "A colorful CLI tool")  # doctest: +SKIP
>>> cli_info("Loading data...")  # doctest: +SKIP
>>> cli_success("Done!")  # doctest: +SKIP

Author: Eigenscribe
Date: October 2026
Last Updated: November 2026
"""

from __future__ import annotations

import os
import sys
from typing import Any, Final

# Force UTF-8 stdout on Windows to support emoji and Unicode chars
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
elif sys.platform == "win32":
    import io

    try:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
    except Exception:
        pass

# Try to import click; fall back to raw print if not available
try:
    import click

    _HAS_CLICK = True
except ImportError:
    _HAS_CLICK = False

# Try to import tabulate; fall back to basic formatting if not available
try:
    from tabulate import tabulate

    _HAS_TABULATE = True
except ImportError:
    _HAS_TABULATE = False

# Import gradient engine components
try:
    from the_scriber_experience.cli.gradient import (
        PRESETS,
        RGB,
        Color,
        hex_to_rgb,
        multi_gradient,
    )
except ImportError:
    try:
        from .gradient import (
            PRESETS,
            RGB,
            Color,
            hex_to_rgb,
            multi_gradient,
        )
    except ImportError:
        PRESETS = {
            "electric": ("#00a6ff", "#a855f7", "#ff00c3"),
        }
        RGB = tuple[int, int, int]
        Color = str | RGB

        def hex_to_rgb(hex_color: str) -> RGB:
            v = hex_color.removeprefix("#")
            return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)

        def multi_gradient(
            text: str, colors: Any = PRESETS["electric"], *, bold: bool = True
        ) -> str:
            prefix = "\033[1m" if bold else ""
            return f"{prefix}{text}\033[0m"


__all__: list[str] = [
    # Core messaging
    "cli_message",
    "cli_echo",
    "cli_rule",
    "cli_banner",
    "cli_table",
    "cli_divider",
    "cli_section",
    "cli_prompt",
    # Semantic levels
    "cli_info",
    "cli_success",
    "cli_warning",
    "cli_error",
    "cli_highlight",
    "cli_network",
    "cli_quantum",
    "cli_rotor",
    # Gradients & Colors
    "multi_gradient",
    "PRESETS",
    "Color",
    "RGB",
    "hex_to_rgb",
    # Color palette access
    "EIGENSCRIBE_PALETTE",
    "STYLE_MAP",
    "SEMANTIC_SYMBOLS",
    "ansi_256",
    "supports_256_color",
]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 Definitions, Constants & Types — Eigenscribe 256-Color Palette
# -----------------------------------------------------------------------------------------------------------

# Eigenscribe brand palette mapped to ANSI 256-color indices
EIGENSCRIBE_PALETTE: Final[dict[str, int]] = {
    # Blues (primary focus / headers)
    "eigen_blue": 39,  # Vibrant Deep Sky Blue (#00afff)
    "eigen_blue_bright": 33,  # Dodger Blue (#0087ff)
    "eigen_blue_dark": 27,  # Deep Royal Blue (#005fff)
    "eigen_cyan": 51,  # Electric Cyan (#00ffff)
    "eigen_cyan_light": 45,  # Bright Sky Cyan (#00d7ff)
    "eigen_cyan_dark": 38,  # Deep Aqua (#00afd7)
    # Purples / Violets (structure / logic)
    "eigen_purple": 141,  # Lavender Violet (#af87ff)
    "eigen_purple_bright": 135,  # Medium Purple (#af5fff)
    "eigen_purple_dark": 99,  # Dark Slate Blue (#875fff)
    "eigen_violet": 129,  # Vivid Violet (#af00ff)
    "eigen_indigo": 63,  # Royal Indigo (#5f5fff)
    # Pinks / Magentas (accents / highlights)
    "eigen_pink": 207,  # Hot Pink / Magenta (#ff5fff)
    "eigen_pink_bright": 201,  # Pure Electric Magenta (#ff00ff)
    "eigen_pink_soft": 213,  # Soft Orchid Pink (#ff87ff)
    "eigen_rose": 198,  # Rose Red (#ff0087)
    # Status Colors
    "eigen_green": 48,  # Spring Green (#00ff87)
    "eigen_green_bright": 46,  # Neon Emerald (#00ff00)
    "eigen_green_dark": 34,  # Deep Forest Green (#00af00)
    "eigen_orange": 208,  # Dark Orange (#ff8700)
    "eigen_amber": 214,  # Gold Amber (#ffaf00)
    "eigen_yellow": 226,  # Bright Pure Yellow (#ffff00)
    "eigen_red": 196,  # Bright Signal Red (#ff0000)
    "eigen_red_bright": 160,  # Crimson Red (#d70000)
    # Neutrals / Surfaces
    "eigen_white": 231,  # Pure Crisp White (#ffffff)
    "eigen_cream": 230,  # Cornsilk Cream (#ffffd7)
    "eigen_gray_light": 252,  # Light Silver (#d0d0d0)
    "eigen_gray": 245,  # Medium Slate Gray (#8a8a8a)
    "eigen_gray_dark": 238,  # Dark Charcoal (#444444)
    "eigen_black": 232,  # Deep Void Black (#080808)
}

# Semantic style mapping (level -> ANSI 256 color key)
STYLE_MAP: Final[dict[str, str]] = {
    "info": "eigen_cyan_light",
    "success": "eigen_green",
    "warning": "eigen_amber",
    "error": "eigen_red",
    "highlight": "eigen_pink",
    "rule": "eigen_gray",
    "banner": "eigen_blue",
    "section": "eigen_purple",
    "network": "eigen_purple_bright",
    "quantum": "eigen_cyan",
    "rotor": "eigen_pink_bright",
}

# Semantic prefix icons
SEMANTIC_SYMBOLS: Final[dict[str, str]] = {
    "info": "ℹ️ ",
    "success": "✅",
    "warning": "⚠️ ",
    "error": "❌",
    "highlight": "✨",
    "network": "🕸️ ",
    "quantum": "⚛️ ",
    "rotor": "🔄",
    "section": "🔷",
}


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API / Core Formatting Functions
# -----------------------------------------------------------------------------------------------------------


def supports_256_color() -> bool:
    """
    Check if the current terminal supports 256-color ANSI escape sequences.

    Returns
    -------
    bool
        True if the terminal supports 256 colors, False for 16-color fallback.
    """
    if os.environ.get("NO_COLOR"):
        return False

    term = os.environ.get("TERM", "").lower()
    colorterm = os.environ.get("COLORTERM", "").lower()

    if colorterm in ("truecolor", "24bit", "yes"):
        return True

    if "256color" in term or "256" in term:
        return True

    if sys.platform == "win32":
        if os.environ.get("WT_SESSION"):  # Windows Terminal
            return True
        if os.environ.get("ConEmuPID"):  # ConEmu
            return True
        if os.environ.get("ANSICON"):  # ANSICON
            return True
        # Modern Windows 10+ cmd/powershell typically supports ANSI
        return True

    return bool(term and term != "dumb")


def ansi_256(
    color_key: str, text: str, *, bold: bool = False, underline: bool = False
) -> str:
    """
    Format text with an Eigenscribe 256-color ANSI code.

    Parameters
    ----------
    color_key : str
        Key from EIGENSCRIBE_PALETTE (e.g. 'eigen_cyan', 'eigen_purple').
    text : str
        The text to colorize.
    bold : bool, default=False
        Whether to make the text bold.
    underline : bool, default=False
        Whether to underline the text.

    Returns
    -------
    str
        Text wrapped in ANSI escape sequences, or plain text if unsupported.
    """
    if not supports_256_color():
        return text

    code = EIGENSCRIBE_PALETTE.get(color_key)
    if code is None:
        return text

    style_codes: list[str] = [f"38;5;{code}"]
    if bold:
        style_codes.append("1")
    if underline:
        style_codes.append("4")

    joined = ";".join(style_codes)
    return f"\033[{joined}m{text}\033[0m"


def cli_echo(message: str, *, color: str | None = None, bold: bool = False) -> None:
    """
    Print a message to stdout with optional 256-color styling.

    Parameters
    ----------
    message : str
        Message to print.
    color : str, optional
        Color key from EIGENSCRIBE_PALETTE.
    bold : bool, default=False
        Whether to render bold text.
    """
    if color and supports_256_color():
        out = ansi_256(color, message, bold=bold)
    else:
        out = message

    if _HAS_CLICK:
        click.echo(out, color=True)
    else:
        print(out)


def cli_message(
    level: str,
    message: str,
    *,
    prefix: bool = True,
    bold: bool = False,
) -> None:
    """
    Print a semantic CLI message using Eigenscribe color hierarchies.

    Parameters
    ----------
    level : str
        One of 'info', 'success', 'warning', 'error', 'highlight', 'network', 'quantum', 'rotor'.
    message : str
        The message content.
    prefix : bool, default=True
        Whether to include the semantic emoji prefix.
    bold : bool, default=False
        Whether the message body should be bold.
    """
    color_key = STYLE_MAP.get(level, "eigen_white")
    icon = SEMANTIC_SYMBOLS.get(level, "") if prefix else ""
    full_text = f"{icon} {message}".strip()

    if supports_256_color():
        styled = ansi_256(color_key, full_text, bold=bold)
        if _HAS_CLICK:
            click.echo(styled, color=True)
        else:
            print(styled)
    else:
        fallback_colors: dict[str, str] = {
            "info": "bright_cyan",
            "success": "bright_green",
            "warning": "bright_yellow",
            "error": "bright_red",
            "highlight": "bright_magenta",
            "network": "bright_magenta",
            "quantum": "bright_cyan",
            "rotor": "bright_magenta",
        }
        fg = fallback_colors.get(level, "white")
        if _HAS_CLICK:
            click.secho(full_text, fg=fg, bold=bold)
        else:
            print(full_text)


def cli_info(message: str, *, bold: bool = False) -> None:
    """Print an informational message in Bright Sky Cyan."""
    cli_message("info", message, bold=bold)


def cli_success(message: str, *, bold: bool = True) -> None:
    """Print a success confirmation message in Neon Spring Green."""
    cli_message("success", message, bold=bold)


def cli_warning(message: str, *, bold: bool = False) -> None:
    """Print a warning message in Gold Amber."""
    cli_message("warning", message, bold=bold)


def cli_error(message: str, *, bold: bool = True) -> None:
    """Print an error alert message in Bright Signal Red."""
    cli_message("error", message, bold=bold)


def cli_highlight(message: str, *, bold: bool = True) -> None:
    """Print a high-attention highlight in Pure Electric Magenta."""
    cli_message("highlight", message, bold=bold)


def cli_network(message: str, *, bold: bool = False) -> None:
    """Print a network topology cue in Medium Purple."""
    cli_message("network", message, bold=bold)


def cli_quantum(message: str, *, bold: bool = False) -> None:
    """Print a quantum execution cue in Electric Cyan."""
    cli_message("quantum", message, bold=bold)


def cli_rotor(message: str, *, bold: bool = False) -> None:
    """Print a Clifford GA rotor cue in Pure Electric Magenta."""
    cli_message("rotor", message, bold=bold)


def cli_section(title: str) -> None:
    """
    Print a styled section header.

    Parameters
    ----------
    title : str
        Section title string.
    """
    rule = "─" * (len(title) + 6)
    if supports_256_color():
        click.echo("") if _HAS_CLICK else print("")
        cli_echo(rule, color="eigen_purple_dark")
        cli_echo(f"  🔷 {title}", color="eigen_purple_bright", bold=True)
        cli_echo(rule, color="eigen_purple_dark")
    else:
        if _HAS_CLICK:
            click.secho(f"\n--- {title} ---", fg="bright_magenta", bold=True)
        else:
            print(f"\n--- {title} ---")


def cli_rule(
    char: str = "─",
    width: int = 60,
    *,
    level: str = "rule",
) -> None:
    """
    Print a decorative horizontal rule.

    Parameters
    ----------
    char : str, default='─'
        Character used for the rule line.
    width : int, default=60
        Width of the rule in characters.
    level : str, default='rule'
        Color level from STYLE_MAP.
    """
    color_key = STYLE_MAP.get(level, "eigen_gray")
    line = char * width
    cli_echo(line, color=color_key)


def cli_divider(title: str = "", width: int = 60) -> None:
    """
    Print a centered divider with optional title text.

    Parameters
    ----------
    title : str, optional
        Title centered on the divider line.
    width : int, default=60
        Total width of the divider.
    """
    if not title:
        cli_rule(char="─", width=width)
        return

    pad = max(2, (width - len(title) - 4) // 2)
    left = "─" * pad
    right = "─" * (width - len(title) - pad - 2)
    line = f"{left} {title} {right}"
    cli_echo(line, color="eigen_purple_bright", bold=True)


def cli_banner(
    title: str,
    subtitle: str | None = None,
    *,
    width: int = 60,
    preset: str = "electric",
) -> None:
    """
    Print a prominent application banner with TrueColor gradient styling.

    Parameters
    ----------
    title : str
        Main banner title.
    subtitle : str, optional
        Secondary explanatory text.
    width : int, default=60
        Banner width.
    preset : str, default='electric'
        Gradient preset name from PRESETS.
    """
    cli_echo("")
    top_bar = "═" * width
    cli_echo(top_bar, color="eigen_blue_bright", bold=True)

    # Gradient title
    colors = PRESETS.get(preset, PRESETS["electric"])
    gradient_title = multi_gradient(
        f"  {title.center(width - 4)}  ", colors=colors, bold=True
    )
    if _HAS_CLICK:
        click.echo(gradient_title, color=True)
    else:
        print(gradient_title)

    if subtitle:
        cli_echo(
            f"  {subtitle.center(width - 4)}  ", color="eigen_cyan_light", bold=False
        )

    bottom_bar = "═" * width
    cli_echo(bottom_bar, color="eigen_blue_bright", bold=True)
    cli_echo("")


def cli_table(
    data: list[dict[str, Any]] | list[list[Any]],
    headers: list[str] | str = "keys",
    title: str | None = None,
) -> None:
    """
    Print a formatted table using rounded grid styling and brand colors.

    Parameters
    ----------
    data : list[dict[str, Any]] or list[list[Any]]
        Records or matrix to display.
    headers : list[str] or "keys", default="keys"
        Table column headers.
    title : str, optional
        Optional table title.
    """
    if title:
        cli_echo(f"\n-- {title} --", color="eigen_cyan", bold=True)

    if _HAS_TABULATE:
        rendered = tabulate(data, headers=headers, tablefmt="rounded_grid")
        if _HAS_CLICK:
            click.echo(rendered, color=True)
        else:
            print(rendered)
    else:
        print(data)


def cli_prompt(prompt_text: str, default: str | None = None) -> str:
    """
    Prompt the user for input with Eigenscribe cyan styling.

    Parameters
    ----------
    prompt_text : str
        Prompt string shown to user.
    default : str, optional
        Default value returned if user presses enter.

    Returns
    -------
    str
        User input string.
    """
    styled_prompt = ansi_256("eigen_cyan", f"❓ {prompt_text}", bold=True)
    if default:
        styled_prompt += ansi_256("eigen_gray_light", f" [{default}]")
    styled_prompt += ": "

    if _HAS_CLICK:
        return click.prompt(styled_prompt, default=default or "", show_default=False)
    else:
        res = input(styled_prompt)
        return res if res else (default or "")


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Validate all messaging functions and color palettes."""
    print("💨 Running messaging smoke test...")

    assert len(EIGENSCRIBE_PALETTE) >= 20
    assert "eigen_blue" in EIGENSCRIBE_PALETTE
    assert "eigen_cyan" in EIGENSCRIBE_PALETTE
    assert "eigen_purple" in EIGENSCRIBE_PALETTE

    cli_banner("TSE MESSAGING", "Smoke Test Validation", width=50)
    cli_info("Informational message verification.")
    cli_success("Success message verification.")
    cli_warning("Warning message verification.")
    cli_error("Error message verification.")
    cli_highlight("Highlight message verification.")
    cli_network("Network message verification.")
    cli_quantum("Quantum message verification.")
    cli_rotor("Rotor message verification.")
    cli_rule(width=50)
    cli_table([{"Key": "Status", "Value": "Active"}], title="Test Table")

    print("✅ Messaging smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point for standalone execution."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
