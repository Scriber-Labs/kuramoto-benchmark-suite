"""
gradients.py

TrueColor gradient engine and preset definitions.

Author: Eigenscribe
Date: November 20, 2026
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

from scriber_core.frontend.colors import COLOR_PALETTE
from scriber_core.frontend.gradients import GRADIENT_PRESETS

from kuramoto.cli.style.color_utils import _normalize_color
from kuramoto.cli.style.types import Color

__all__: list[str] = [
    "PRESETS",
    "multi_gradient",
    "cli_gradient",
]


# -----------------------------------------------------------------------------------------------------------
# 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------


PRESETS: Final[dict[str, tuple[str, ...]]] = {
    # 🐉 Signature Eigenscribe (without pink): Blue (#0a95eb) -> Periwinkle (#5280ff) -> Purple (#a855f7)
    "eigenscribe-1": (
        COLOR_PALETTE["sky_info"],
        COLOR_PALETTE["skyline_blue"],
        COLOR_PALETTE["periwinkle_blue"],
        COLOR_PALETTE["node-7"],
    ),
    # 🌟 Signature Eigenscribe (with pink): Blue (#00a6ff) -> Purple (#a855f7) -> Magenta (#ff00c3)
    "eigenscribe-2": (
        COLOR_PALETTE["node-2"],
        COLOR_PALETTE["eigen_blue"],
        COLOR_PALETTE["midwest_indigo"],
        COLOR_PALETTE["node-7"],
    ),
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
    # 💚 Green Gradient
    "green_gradient": (GRADIENT_PRESETS["green_gradient"]),
    # 💜 Purple Gradient:
    "purple_gradient": (GRADIENT_PRESETS["purple_gradient"]),
}


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API
# -----------------------------------------------------------------------------------------------------------


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


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke Tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for gradient engine."""
    print("💨 Running gradients.py smoke tests...")

    # Test multi_gradient
    grad = multi_gradient("Test Gradient", PRESETS["electric"])
    assert "\033[0m" in grad
    assert cli_gradient("Alias Test") != ""

    # Test empty text
    assert multi_gradient("") == ""

    # Test preset lookup
    assert "eigenscribe-1" in PRESETS
    assert "purple_gradient" in PRESETS

    print("✅ gradients.py smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry Point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Run smoke tests for the gradients module."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
