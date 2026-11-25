"""
src/kuramoto/cli/style

Semantic CLI output styling — re-exports from scriber_core for common messaging,
plus domain-specific extensions (network, quantum, rotor, ZBW, coprime) and
gradient presets unique to the Kuramoto Benchmark Suite.

Author: Eigenscribe
Date: November 2026
"""

from __future__ import annotations

# Re-exports from scriber_core — canonical messaging, palettes, and color utilities
from eigenscribe.cli.messaging import (
    EIGENSCRIBE_PALETTE,
    STYLE_MAP,
    ansi_256,
    cli_banner,
    cli_echo,
    cli_error,
    cli_highlight,
    cli_info,
    cli_message,
    cli_rule,
    cli_success,
    cli_warning,
    multi_gradient,
    supports_256_color,
)
from eigenscribe.frontend.colors import COLOR_PALETTE, Color, RGB, hex_to_rgb


# Local implementations for functions not yet in scriber_core
def cli_section(title: str) -> None:
    """Print a section header with decorative borders."""
    import click
    border = "─" * 50
    click.echo("")
    click.secho(f" {border}", fg="bright_white", bold=True)
    click.secho(f"  {title}", fg="bright_white", bold=True)
    click.secho(f" {border}", fg="bright_white", bold=True)


def cli_divider() -> None:
    """Print a simple horizontal divider line."""
    import click
    click.secho(" ─" * 25, fg="bright_white")

# Domain-specific extensions — kuramoto-only semantic messages
from .domain import (
    CRT_CHANNEL_A_COLOR,
    CRT_CHANNEL_B_COLOR,
    style_coprime_coeff,
    style_coprime_gcd,
    style_coprime_remainder,
    style_coprime_term,
    style_crt_channel,
)
from .gradients import (
    PRESETS,
    cli_gradient,
)
from .messages import (
    cli_coprime,
    cli_network,
    cli_quantum,
    cli_rotor,
    cli_zbw,
)

# Legacy alias for backward compatibility
ANSI_256_PALETTE = EIGENSCRIBE_PALETTE
print_hex_swatches = hex_to_rgb  # stub — hex_to_rgb is the canonical function

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
    "CRT_CHANNEL_A_COLOR",
    "CRT_CHANNEL_B_COLOR",
    "style_coprime_term",
    "style_coprime_gcd",
    "style_coprime_coeff",
    "style_coprime_remainder",
    "style_crt_channel",
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
    remainder = style_coprime_remainder(3)
    assert "7" in term and "1" in gcd_str and "-3" in coeff and "3" in remainder

    print("✅ Style smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point for standalone execution."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
