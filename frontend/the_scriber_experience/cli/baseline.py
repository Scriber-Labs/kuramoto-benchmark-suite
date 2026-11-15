# frontend/the_scriber_experience/cli/baseline.py
"""
baseline.py

Baseline Command-Line User Interface (CLI) for The Scriber Experience (TSE).
Provides a reference implementation of a branded, ADHD-friendly, high-contrast
terminal interface with multi-stop linear gradients, semantic messaging levels,
interactive menus, tabular summaries, and command-dispatching.

Usage
-----
Run directly as a script or module:
$ python -m the_scriber_experience.cli.baseline --help
$ python -m the_scriber_experience.cli.baseline interactive

Or import into external applications:
>>> from the_scriber_experience.cli.baseline import run_baseline_demo, BaselineCLI
>>> cli = BaselineCLI(app_name="My Scientific Tool", version="1.0.0")
>>> cli.render_welcome()

Author: Eigenscribe
Date: November 2026
"""

from __future__ import annotations

import argparse
from typing import Any, Final

# Try to import click
try:
    import click

    _HAS_CLICK = True
except ImportError:
    _HAS_CLICK = False

try:
    from the_scriber_experience.cli.gradient import PRESETS, multi_gradient
    from the_scriber_experience.cli.messaging import (
        EIGENSCRIBE_PALETTE,
        ansi_256,
        cli_banner,
        cli_echo,
        cli_error,
        cli_highlight,
        cli_info,
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
except ImportError:
    from .gradient import PRESETS, multi_gradient
    from .messaging import (
        EIGENSCRIBE_PALETTE,
        ansi_256,
        cli_banner,
        cli_echo,
        cli_error,
        cli_highlight,
        cli_info,
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
    "BaselineCLI",
    "run_baseline_demo",
    "show_palette_showcase",
    "show_gradient_presets",
    "show_semantic_levels",
    "show_tabular_demo",
    "run_interactive_menu",
]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------

DEFAULT_APP_NAME: Final[str] = "THE SCRIBER EXPERIENCE"
DEFAULT_TAGLINE: Final[str] = "Baseline CLI User Interface & Semantic Terminal Engine"
DEFAULT_VERSION: Final[str] = "1.0.0"


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API / Baseline CLI Class
# -----------------------------------------------------------------------------------------------------------


class BaselineCLI:
    """
    Baseline CLI manager orchestrating branded terminal output.

    Parameters
    ----------
    app_name : str, default='THE SCRIBER EXPERIENCE'
        Primary application display name.
    tagline : str, default='Baseline CLI User Interface & Semantic Terminal Engine'
        Secondary descriptive banner tagline.
    version : str, default='1.0.0'
        Software semantic version string.
    preset : str, default='electric'
        Gradient preset for main banners.
    width : int, default=64
        Standard line width in characters.
    """

    def __init__(
        self,
        app_name: str = DEFAULT_APP_NAME,
        tagline: str = DEFAULT_TAGLINE,
        version: str = DEFAULT_VERSION,
        preset: str = "electric",
        width: int = 64,
    ) -> None:
        self.app_name = app_name
        self.tagline = tagline
        self.version = version
        self.preset = preset
        self.width = width

    def render_welcome(self) -> None:
        """Render the primary welcome banner and environment summary."""
        cli_banner(
            self.app_name,
            f"{self.tagline} (v{self.version})",
            width=self.width,
            preset=self.preset,
        )

        status_256 = (
            "Enabled (TrueColor/256-color)"
            if supports_256_color()
            else "Fallback (16-color)"
        )
        cli_info(f"Terminal Color Mode: {status_256}")
        cli_info("Eigenscribe 4-Layer Semantic Output Engine: Active")
        cli_rule(char="·", width=self.width)

    def show_all(self) -> None:
        """Execute a full demonstration showcase of all UI elements."""
        self.render_welcome()
        show_semantic_levels(width=self.width)
        show_gradient_presets(width=self.width)
        show_tabular_demo(width=self.width)
        show_palette_showcase(width=self.width)
        cli_success("Full Baseline CLI showcase completed successfully.")


# -----------------------------------------------------------------------------------------------------------
# 2️⃣ UI Showcase Functions & Helpers
# -----------------------------------------------------------------------------------------------------------


def show_semantic_levels(width: int = 64) -> None:
    """Display all semantic message levels with icons and color coding."""
    cli_section("1. Semantic Messaging Levels")
    cli_info("Informational message (Sky Cyan) for neutral progress and logs.")
    cli_success("Success message (Neon Green) for verified milestones and tests.")
    cli_warning("Warning message (Gold Amber) for non-critical alerts or fallbacks.")
    cli_error("Error alert (Signal Red) for exceptions and validation failures.")
    cli_highlight("Highlight cue (Pure Magenta) for key metrics and discoveries.")
    cli_network("Network topology cue (Medium Purple) for graph and matrix states.")
    cli_quantum("Quantum execution cue (Electric Cyan) for SCF and statevectors.")
    cli_rotor("Clifford GA rotor cue (Vivid Magenta) for bivector and Spin(n) steps.")
    cli_rule(char="─", width=width)


def show_gradient_presets(width: int = 64) -> None:
    """Display all multi-stop linear gradient presets."""
    cli_section("2. ANSI TrueColor Gradient Presets")
    for name, stops in PRESETS.items():
        sample_text = f"  [{name.upper()}]  " + "━" * (width - len(name) - 12)
        grad_line = multi_gradient(sample_text, colors=stops, bold=True)
        if _HAS_CLICK:
            click.echo(grad_line, color=True)
        else:
            print(grad_line)
    cli_rule(char="─", width=width)


def show_tabular_demo(width: int = 64) -> None:
    """Display tabular data with rounded grid borders and status metrics."""
    cli_section("3. Tabular Summary & Execution Metrics")
    sample_data: list[dict[str, Any]] = [
        {
            "Subsystem": "Classical ODE (RK45)",
            "Manifold": "R^N Phase Space",
            "Order Param r": "0.9842",
            "Energy Drift": "1.24e-05",
            "Status": "PASSED",
        },
        {
            "Subsystem": "GA Rotor (Spin(2))",
            "Manifold": "Cl_{2,0} Rotor",
            "Order Param r": "0.9915",
            "Energy Drift": "4.12e-07",
            "Status": "PASSED",
        },
        {
            "Subsystem": "Quantum SCF (4-Qubit)",
            "Manifold": "Hilbert Statevector",
            "Order Param r": "0.9410",
            "Energy Drift": "8.80e-06",
            "Status": "PASSED",
        },
        {
            "Subsystem": "Coprime Sub-Nyquist",
            "Manifold": "Dual M/N Strides",
            "Order Param r": "0.9890",
            "Energy Drift": "2.10e-05",
            "Status": "PASSED",
        },
    ]
    cli_table(sample_data, headers="keys", title="Benchmark Solver Invariants")
    cli_rule(char="─", width=width)


def show_palette_showcase(width: int = 64) -> None:
    """Display the full Eigenscribe 256-color palette swatches."""
    cli_section("4. Eigenscribe 256-Color Swatch Palette")
    rows: list[dict[str, str]] = []
    for key, code in EIGENSCRIBE_PALETTE.items():
        swatch = ansi_256(key, f" ■■■ {key:<18} (Code {code:>3}) ■■■ ", bold=True)
        rows.append({"Color Name": key, "ANSI Code": str(code), "Swatch": swatch})

    # Render as formatted rows
    for r in rows:
        if _HAS_CLICK:
            click.echo(f"  {r['Swatch']}", color=True)
        else:
            print(f"  {r['Swatch']}")
    cli_rule(char="─", width=width)


def run_interactive_menu() -> None:
    """Run an interactive CLI menu loop for user navigation."""
    cli = BaselineCLI()
    cli.render_welcome()

    while True:
        cli_echo(
            "\n📌 Select a demonstration mode:", color="eigen_purple_bright", bold=True
        )
        cli_echo("  1. Semantic Messaging Levels", color="eigen_cyan_light")
        cli_echo("  2. ANSI TrueColor Gradients", color="eigen_cyan_light")
        cli_echo("  3. Tabular Summary Matrix", color="eigen_cyan_light")
        cli_echo("  4. Eigenscribe Color Swatches", color="eigen_cyan_light")
        cli_echo("  5. Full System Showcase", color="eigen_cyan_light")
        cli_echo("  0. Exit", color="eigen_gray")

        choice = cli_prompt("Enter choice [0-5]", default="5").strip()

        if choice == "1":
            show_semantic_levels()
        elif choice == "2":
            show_gradient_presets()
        elif choice == "3":
            show_tabular_demo()
        elif choice == "4":
            show_palette_showcase()
        elif choice == "5":
            cli.show_all()
        elif choice in ("0", "q", "quit", "exit"):
            cli_success("Exiting Baseline CLI. Goodbye!")
            break
        else:
            cli_warning(f"Invalid option '{choice}'. Please select 0 to 5.")


def run_baseline_demo() -> None:
    """Run the non-interactive standard baseline demo."""
    cli = BaselineCLI()
    cli.show_all()


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Sanity test for BaselineCLI components."""
    print("💨 Running baseline CLI smoke test...")
    cli = BaselineCLI(width=50)
    assert cli.app_name == DEFAULT_APP_NAME
    assert cli.version == DEFAULT_VERSION

    # Test all showcase functions
    cli.render_welcome()
    show_semantic_levels(width=50)
    show_gradient_presets(width=50)
    show_tabular_demo(width=50)
    print("✅ Baseline CLI smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """CLI Entry Point."""
    parser = argparse.ArgumentParser(
        description="The Scriber Experience (TSE) Baseline CLI User Interface"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="showcase",
        choices=[
            "showcase",
            "interactive",
            "palette",
            "gradient",
            "semantic",
            "table",
            "smoke-test",
        ],
        help="Command to run (default: showcase)",
    )

    args = parser.parse_args()

    if args.command == "smoke-test":
        _run_smoke_test()
    elif args.command == "interactive":
        run_interactive_menu()
    elif args.command == "palette":
        show_palette_showcase()
    elif args.command == "gradient":
        show_gradient_presets()
    elif args.command == "semantic":
        show_semantic_levels()
    elif args.command == "table":
        show_tabular_demo()
    else:
        run_baseline_demo()


if __name__ == "__main__":
    main()
