# src/kuramoto/cli/style/palettes.py
"""
palettes.py

Static color maps and palette definitions.

Author: Eigenscribe
Date: November 20, 2026
"""

from __future__ import annotations

from typing import Final

from scriber_core.frontend.colors import COLOR_PALETTE as SCRIBER_CORE_COLOR_PALETTE

__all__: list[str] = [
    "STYLE_MAP",
    "COLOR_PALETTE",
    "ANSI_256_PALETTE",
    "EIGENSCRIBE_PALETTE",
]

# -----------------------------------------------------------------------------------------------------------
# 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------

STYLE_MAP: Final[dict[str, str]] = {
    "info": SCRIBER_CORE_COLOR_PALETTE["sky_info"],
    "network": SCRIBER_CORE_COLOR_PALETTE["vivid_pink"],
    "quantum": SCRIBER_CORE_COLOR_PALETTE["node-6"],
    "rotor": SCRIBER_CORE_COLOR_PALETTE["eigen_blue"],
    "zbw": SCRIBER_CORE_COLOR_PALETTE["periwinkle_blue"],
    "coprime": SCRIBER_CORE_COLOR_PALETTE["electric_blue"],
    "success": SCRIBER_CORE_COLOR_PALETTE["deep_green"],
    "warning": SCRIBER_CORE_COLOR_PALETTE["golden_amber"],
    "error": SCRIBER_CORE_COLOR_PALETTE["ibm_pink"],
    "highlight": SCRIBER_CORE_COLOR_PALETTE["bright_magenta"],
    "section": SCRIBER_CORE_COLOR_PALETTE["ibm_white"]
}

# Extended color palette for richer output (local copy for backwards compatibility)
COLOR_PALETTE: Final[dict[str, str]] = {
    "cyan": SCRIBER_CORE_COLOR_PALETTE["sky_cyan"],
    "magenta": SCRIBER_CORE_COLOR_PALETTE["vivid_pink"],
    "green": SCRIBER_CORE_COLOR_PALETTE["slime_green"],
    "yellow": SCRIBER_CORE_COLOR_PALETTE["golden_amber"],
    "red": SCRIBER_CORE_COLOR_PALETTE["error_crimson"],
    "blue": SCRIBER_CORE_COLOR_PALETTE["eigen_blue"],
    "white": SCRIBER_CORE_COLOR_PALETTE["ibm_white"],
    "bright_cyan": SCRIBER_CORE_COLOR_PALETTE["bright_cyan"],
    "bright_magenta": SCRIBER_CORE_COLOR_PALETTE["bright_magenta"],
    "bright_green": SCRIBER_CORE_COLOR_PALETTE["neon_green"],
    "bright_yellow": SCRIBER_CORE_COLOR_PALETTE["apricot"],
    "bright_blue": SCRIBER_CORE_COLOR_PALETTE["electric_blue"],
    "bright_white": SCRIBER_CORE_COLOR_PALETTE["ghost_white"],
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
# 💨 Smoke Tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Verify palette definitions and print colored swatches."""
    import click
    try:
        from .color_utils import print_hex_swatches
    except ImportError:
        from kuramoto.cli.style.color_utils import print_hex_swatches

    print("👟 💨 Running palettes.py smoke tests...")

    # Validate structures
    assert len(STYLE_MAP) > 0
    assert "info" in STYLE_MAP
    assert len(COLOR_PALETTE) > 0
    assert len(ANSI_256_PALETTE) > 0
    assert EIGENSCRIBE_PALETTE is ANSI_256_PALETTE

    # Print swatches using shared helper
    print_hex_swatches("STYLE_MAP", STYLE_MAP, width=12)
    print_hex_swatches("COLOR_PALETTE", COLOR_PALETTE, width=16)

    # ANSI_256_PALETTE uses 256-color codes, not hex
    click.echo("")
    click.secho(" 🎨 ANSI_256_PALETTE Swatches:", fg="bright_white", bold=True, color=True)
    for name, code in ANSI_256_PALETTE.items():
        click.echo(f"  {name:20s} ", nl=False)
        click.echo(f"\033[38;5;{code}m{'█' * 10}\033[0m", color=True)

    click.echo("")
    print("✅ 💨 palettes.py smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry Point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Run smoke tests for the palettes module."""
    _run_smoke_test()

if __name__ == "__main__":
    main()