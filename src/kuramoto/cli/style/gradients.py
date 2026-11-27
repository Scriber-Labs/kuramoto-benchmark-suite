"""
gradients.py

Kuramoto-specific gradient presets extending scriber_core's gradient engine.

Author: Eigenscribe
Date: November 20, 2026
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

from eigenscribe.frontend.colors import COLOR_PALETTE, Color
from eigenscribe.frontend.gradients import GRADIENT_PRESETS
from eigenscribe.frontend.gradients import multi_gradient as _multi_gradient

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
    "eigenscribe": (
        COLOR_PALETTE["node-2"],
        COLOR_PALETTE["eigen_blue"],
        COLOR_PALETTE["midwest_indigo"],
        COLOR_PALETTE["node-7"],
    ),
    "electric": GRADIENT_PRESETS["electric"],
    "tse-gradient-1": (
        COLOR_PALETTE["electric_lagoon"],
        COLOR_PALETTE["reef_cyan"],
        COLOR_PALETTE["cerulean_surge"],
        COLOR_PALETTE["royal_blue"],
        COLOR_PALETTE["twilight_indigo"],
        COLOR_PALETTE["dusk_violet_blue"],
        COLOR_PALETTE["cosmic_iris"],
        COLOR_PALETTE["nebula_purple"],
        COLOR_PALETTE["neon_orchid"],
    ),
    # 🌟 Signature Eigenscribe (with pink): Blue (#00a6ff) -> Purple (#a855f7) -> Magenta (#ff00c3)
    "tse-gradient-2": GRADIENT_PRESETS["tse-gradient-2"],
    # 🌅 Solar Sunset: Orange (#ff6b35) -> Amber (#f7c548) -> Crimson (#d7263d)
    "sunset": ("#ff6b35", "#f7c548", "#ff40a1"),
    # 🌲 Deep Forest: Olive (#a7c957) -> Teal (#2a9d8f) -> Pine (#264653)
    "forest": ("#a7c957", "#2a9d8f", "#264653"),
    # 🌌 Midnight Cosmic: Sky Cyan (#38bdf8) -> Lavender (#818cf8) -> Rose (#f43f5e)
    "midnight": ("#38bdf8", "#818cf8", "#f43f5e"),
    # 🌿 Quantum Aurora: Aqua (#06b6d4) -> Emerald (#10b981) -> Lime (#84cc16)
    "aurora": ("#06b6d4", "#10b981", "#84cc16"),
    # 🩵💙 Blue Gradient
    "blue_gradient": (GRADIENT_PRESETS["blue_gradient"]),
    # 💚 Green Gradient
    "green_gradient": (GRADIENT_PRESETS["green_gradient"]),
    # 💜 Purple Gradient:
    "purple_gradient": (GRADIENT_PRESETS["purple_gradient"]),
}


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API — delegates to scriber_core gradient engine
# -----------------------------------------------------------------------------------------------------------


def multi_gradient(
    text: str,
    colors: Sequence[Color] = GRADIENT_PRESETS["eigenscribe"],
    *,
    bold: bool = True,
) -> str:
    """
    Return text formatted with an ANSI TrueColor gradient across multiple color stops.

    Delegates to scriber_core's gradient engine.

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
    return _multi_gradient(text, colors=colors, bold=bold)


# Canonical alias
cli_gradient = multi_gradient


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke Tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for gradient engine."""
    print("💨 Running gradients.py smoke tests...")

    # Test multi_gradient
    grad = multi_gradient("Test Gradient", PRESETS["aurora"])
    assert "\033[0m" in grad
    assert cli_gradient("Alias Test") != ""

    # Test empty text
    assert multi_gradient("") == ""

    # Test preset lookup
    assert "eigenscribe" in PRESETS
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
