# frontend/the_scriber_experience/cli/__init__.py
"""
cli

CLI styling, gradient engine, semantic messaging, and baseline user interface
modules for The Scriber Experience (TSE).
"""

from __future__ import annotations

from the_scriber_experience.cli.baseline import (
    BaselineCLI,
    run_baseline_demo,
    run_interactive_menu,
    show_gradient_presets,
    show_palette_showcase,
    show_semantic_levels,
    show_tabular_demo,
)
from the_scriber_experience.cli.gradient import (
    PRESETS,
    RGB,
    Color,
    hex_to_rgb,
    interpolate_rgb,
    multi_gradient,
    rgb_to_hex,
)
from the_scriber_experience.cli.messaging import (
    EIGENSCRIBE_PALETTE,
    SEMANTIC_SYMBOLS,
    STYLE_MAP,
    ansi_256,
    cli_banner,
    cli_divider,
    cli_echo,
    cli_error,
    cli_highlight,
    cli_info,
    cli_message,
    cli_network,
    cli_prompt,
    cli_quantum,
    cli_rotor,
    cli_rule,
    cli_section,
    cli_success,
    cli_table,
    cli_warning,
    supports_256_color,
)

__all__: list[str] = [
    # Gradient Engine
    "multi_gradient",
    "PRESETS",
    "RGB",
    "Color",
    "hex_to_rgb",
    "rgb_to_hex",
    "interpolate_rgb",
    # Semantic Messaging
    "cli_message",
    "cli_echo",
    "cli_rule",
    "cli_banner",
    "cli_table",
    "cli_divider",
    "cli_section",
    "cli_prompt",
    "cli_info",
    "cli_success",
    "cli_warning",
    "cli_error",
    "cli_highlight",
    "cli_network",
    "cli_quantum",
    "cli_rotor",
    "EIGENSCRIBE_PALETTE",
    "STYLE_MAP",
    "SEMANTIC_SYMBOLS",
    "ansi_256",
    "supports_256_color",
    # Baseline UI
    "BaselineCLI",
    "run_baseline_demo",
    "run_interactive_menu",
    "show_palette_showcase",
    "show_gradient_presets",
    "show_semantic_levels",
    "show_tabular_demo",
]
