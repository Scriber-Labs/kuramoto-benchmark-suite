# src/cli/style/types.py
"""
types.py

Type aliases used across the kuramoto CLI style package.

Author: Eigenscribe
Date: November 20, 2026
"""

from __future__ import annotations

from typing import TypeAlias

__all__: list[str] = [
    "RGB",
    "Color",
]

# -----------------------------------------------------------------------------------------------------------
# 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------

RGB: TypeAlias = tuple[int, int, int]
"""An RGB color represented as a tuple of three integers (0-255)."""

Color: TypeAlias = str | RGB
"""A terminal color, either a hex string (e.g., `#ff6b35`) or an RGB tuple."""


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke Tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for type aliases."""
    rgb: RGB = (255, 128, 0)
    color_hex: Color = "#ff6b35"
    color_rgb: Color = (255, 107, 53)

    assert isinstance(rgb, tuple) and len(rgb) == 3
    assert all(0 <= c <= 255 for c in rgb)
    assert isinstance(color_hex, str)
    assert isinstance(color_rgb, tuple)
    print("✅ 💨 types.py smoke test passed")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry Point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Run smoke tests for the types module."""
    _run_smoke_test()

if __name__ == "__main__":
    main()