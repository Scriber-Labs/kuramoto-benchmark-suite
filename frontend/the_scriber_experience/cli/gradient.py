# frontend/the_scriber_experience/cli/gradient.py
"""
gradient.py

ANSI TrueColor multi-stop linear RGB gradient engine for terminal output.
Provides multi-keyframe color interpolation across six-digit hex codes and RGB
tuples, along with curated Eigenscribe brand gradient presets (electric, sunset,
forest, midnight, aurora, cyberpunk, eigenscribe-1, eigenscribe-2).

Part of The Scriber Experience (TSE) design system.

Usage
-----
>>> from the_scriber_experience.cli.gradient import multi_gradient, PRESETS
>>> print(multi_gradient("Electric Gradient", PRESETS["electric"]))  # doctest: +SKIP
>>> print(multi_gradient("Custom Stops", ["#00a6ff", "#a855f7", "#ff00c3"]))  # doctest: +SKIP

Author: Eigenscribe
Date: October 2026
Last Updated: November 2026
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from typing import Final, TypeAlias

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

__all__: list[str] = [
    "RGB",
    "Color",
    "PRESETS",
    "hex_to_rgb",
    "multi_gradient",
    "rgb_to_hex",
    "interpolate_rgb",
]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------

RGB: TypeAlias = tuple[int, int, int]
Color: TypeAlias = str | RGB

PRESETS: Final[dict[str, tuple[str, ...]]] = {
    # 🌟 Signature Eigenscribe (Electric Cyan -> Purple -> Hot Pink)
    "electric": ("#00a6ff", "#a855f7", "#ff00c3"),
    # 🐉 Eigenscribe Cosmic (Sky Cyan -> Royal Blue -> Indigo -> Deep Violet)
    "eigenscribe-1": ("#38bdf8", "#0A95EB", "#5280ff", "#5e17eb"),
    # 🌟 Eigenscribe Vibrant (Neon Cyan -> Purple -> Magenta)
    "eigenscribe-2": ("#00a6ff", "#a855f7", "#ff00c3"),
    # 🌅 Solar Sunset (Orange -> Amber -> Crimson)
    "sunset": ("#ff6b35", "#f7c548", "#ff40a1"),
    # 🌲 Deep Forest (Olive -> Teal -> Pine)
    "forest": ("#a7c957", "#2a9d8f", "#264653"),
    # 🌌 Midnight Cosmic (Sky Cyan -> Lavender -> Rose)
    "midnight": ("#38bdf8", "#818cf8", "#f43f5e"),
    # 🌿 Quantum Aurora (Aqua -> Emerald -> Lime)
    "aurora": ("#06b6d4", "#10b981", "#84cc16"),
    # ⚡ Cyberpunk Neon (Electric Cyan -> Deep Violet -> Hot Pink)
    "cyberpunk": ("#00f0ff", "#7000ff", "#ff007b"),
    # 💜 Purple Gradient (Soft Violet -> Warm Purple)
    "purple_gradient": ("#7952f5", "#a855f7"),
}


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API / Gradient Engine
# -----------------------------------------------------------------------------------------------------------


def hex_to_rgb(hex_color: str) -> RGB:
    """
    Convert a six-digit hex color string, with or without leading '#', to an (R, G, B) tuple.

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


def rgb_to_hex(rgb: RGB) -> str:
    """
    Convert an (R, G, B) tuple to a normalized six-digit hex string with leading '#'.

    Parameters
    ----------
    rgb : RGB
        Tuple of three integer color channels (0 to 255).

    Returns
    -------
    str
        Formatted hex color string.
    """
    r, g, b = (max(0, min(255, int(c))) for c in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"


def interpolate_rgb(c1: RGB, c2: RGB, factor: float) -> RGB:
    """
    Linearly interpolate between two RGB color tuples.

    Parameters
    ----------
    c1 : RGB
        Starting RGB color.
    c2 : RGB
        Ending RGB color.
    factor : float
        Interpolation weight in [0.0, 1.0].

    Returns
    -------
    RGB
        Interpolated RGB color.
    """
    f = max(0.0, min(1.0, float(factor)))
    return (
        int(round(c1[0] + (c2[0] - c1[0]) * f)),
        int(round(c1[1] + (c2[1] - c1[1]) * f)),
        int(round(c1[2] + (c2[2] - c1[2]) * f)),
    )


def multi_gradient(
    text: str,
    colors: Sequence[Color] = PRESETS["electric"],
    *,
    bold: bool = True,
) -> str:
    """
    Return text formatted with an ANSI TrueColor gradient across multiple color stops.

    Parameters
    ----------
    text : str
        The input text to colorize.
    colors : Sequence[Color], default=PRESETS["electric"]
        A sequence of 2 or more color stops (hex strings or RGB tuples).
    bold : bool, default=True
        Whether to prepend the bold ANSI escape code (SGR 1).

    Returns
    -------
    str
        The formatted string containing ANSI TrueColor escape sequences.

    Raises
    ------
    ValueError
        If fewer than two color stops are provided.
    """
    if not text:
        return ""

    if len(colors) < 2:
        raise ValueError("multi_gradient requires at least two color stops.")

    rgb_stops: list[RGB] = [hex_to_rgb(c) if isinstance(c, str) else c for c in colors]

    total_chars = len(text)
    if total_chars == 1:
        r, g, b = rgb_stops[0]
        prefix = "\033[1m" if bold else ""
        return f"{prefix}\033[38;2;{r};{g};{b}m{text}\033[0m"

    num_segments = len(rgb_stops) - 1
    chars_per_segment = (total_chars - 1) / num_segments

    result_parts: list[str] = []
    if bold:
        result_parts.append("\033[1m")

    for i, char in enumerate(text):
        if char == "\n":
            result_parts.append("\033[0m\n" + ("\033[1m" if bold else ""))
            continue

        segment_idx = min(int(i / chars_per_segment), num_segments - 1)
        segment_start = segment_idx * chars_per_segment
        local_t = (i - segment_start) / chars_per_segment
        local_t = max(0.0, min(1.0, local_t))

        c_start = rgb_stops[segment_idx]
        c_end = rgb_stops[segment_idx + 1]

        r, g, b = interpolate_rgb(c_start, c_end, local_t)
        result_parts.append(f"\033[38;2;{r};{g};{b}m{char}")

    result_parts.append("\033[0m")
    return "".join(result_parts)


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Validate gradient calculations and ANSI escape strings."""
    print("💨 Running gradient engine smoke test...")

    # Hex to RGB
    assert hex_to_rgb("#00a6ff") == (0, 166, 255)
    assert hex_to_rgb("a855f7") == (168, 85, 247)
    assert rgb_to_hex((0, 166, 255)) == "#00a6ff"

    # Multi gradient output
    out = multi_gradient("EIGENSCRIBE", PRESETS["electric"])
    assert "\033[38;2;" in out
    assert "\033[0m" in out
    print(f"Sample Gradient: {out}")

    print("✅ Gradient engine smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Demonstrate gradient generation via CLI."""
    parser = argparse.ArgumentParser(
        description="Eigenscribe TrueColor Gradient Engine"
    )
    parser.add_argument(
        "text", nargs="?", default="THE SCRIBER EXPERIENCE", help="Text to colorize"
    )
    parser.add_argument(
        "--preset",
        choices=list(PRESETS.keys()),
        default="electric",
        help="Color preset",
    )
    parser.add_argument("--no-bold", action="store_true", help="Disable bold text")
    parser.add_argument("--smoke-test", action="store_true", help="Run self-test suite")

    args = parser.parse_args()

    if args.smoke_test:
        _run_smoke_test()
    else:
        print(multi_gradient(args.text, PRESETS[args.preset], bold=not args.no_bold))


if __name__ == "__main__":
    main()
