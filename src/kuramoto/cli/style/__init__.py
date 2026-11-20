"""
src/kuramoto/cli/style

Semantic CLI output styling following Scriber Core and Eigenscribe 4-layer token standards.
Provides consistent contrast-friendly terminal colors for attention support, focal prompts, network topology cues,
quantum execution cues, and invariant verifications.

Author: Eigenscribe
Date: November 2026
"""

from __future__ import annotations

import sys

# Re-exports from submodules (in dependency order)
from .types import Color, RGB

from .palettes import (
    ANSI_256_PALETTE,
    COLOR_PALETTE,
    EIGENSCRIBE_PALETTE,
    STYLE_MAP,
)

from .color_utils import (
    ansi_256,
    hex_to_rgb,
    print_hex_swatches,
    supports_256_color,
)

from .gradients import (
    PRESETS,
    cli_gradient,
    multi_gradient,
)

from .domain import (
    style_coprime_coeff,
    style_coprime_gcd,
    style_coprime_term,
)

from .layout import (
    cli_banner,
    cli_divider,
    cli_echo,
    cli_rule,
    cli_section,
)

from .messages import (
    cli_coprime,
    cli_error,
    cli_highlight,
    cli_info,
    cli_message,
    cli_network,
    cli_quantum,
    cli_rotor,
    cli_success,
    cli_warning,
    cli_zbw,
)

__all__: list[str] = [
    # Types
    "RGB",
    "Color",
    # Palettes
    "STYLE_MAP",
    "COLOR_PALETTE",
    "ANSI_256_PALETTE",
    "EIGENSCRIBE_PALETTE",
    # Color utilities
    "supports_256_color",
    "ansi_256",
    "hex_to_rgb",
    "print_hex_swatches",
    # Gradients
    "multi_gradient",
    "cli_gradient",
    "PRESETS",
    # Domain color helpers
    "style_coprime_term",
    "style_coprime_gcd",
    "style_coprime_coeff",
    # Layout
    "cli_echo",
    "cli_rule",
    "cli_banner",
    "cli_section",
    "cli_divider",
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
]


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke Tests
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
