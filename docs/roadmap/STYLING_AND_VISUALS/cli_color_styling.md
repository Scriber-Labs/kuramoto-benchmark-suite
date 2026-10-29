# CLI Color Styling / Attention Support

## Why this matters

Color styling in the CLI is not just visual polish. It helps with attention, orientation, and quickly distinguishing message types while working in the terminal.

In accordance with `.scriber-core/.junie/AGENTS.md` and Scriber Labs design rules, styling should operate as a cohesive semantic layer aligned with the 4-layer design token taxonomy and ADHD high-contrast semantic spectrum.

---

## Eigenscribe & Scriber Labs Palette Alignment

The canonical semantic tokens map to the CLI color vocabulary as follows:

| Token / Category | Hex / ANSI Truecolor | Semantic Meaning / Role | Click Fallback |
| :--- | :--- | :--- | :--- |
| **Primary Cyan / Electric Blue** | `#00e8ff` / `rgb(0, 232, 255)` | Interactive focal points, info, active state | `cyan` / `bright_cyan` |
| **Secondary Violet / Purple** | `#9b7dff` / `rgb(155, 125, 255)` | Structural markers, network / topology | `bright_magenta` / `magenta` |
| **Tertiary Neon Green** | `#22f792` / `rgb(34, 247, 146)` | Success metrics, verified invariants, math | `bright_green` / `green` |
| **Quaternary Coral / Amber** | `#ff783d` / `rgb(255, 120, 61)` | Warnings, dynamic parameters, cautions | `bright_yellow` / `yellow` |
| **Pernary Hot Pink / Red** | `#ff40a1` / `rgb(255, 64, 161)` | Errors, critical alerts, validation halts | `bright_red` / `red` |

---

## Architectural Goal & Specification

Create a dedicated styling module (`src/kuramoto/cli/style.py`) providing a clean functional API:

```python
from kuramoto.cli.style import (
    cli_info,
    cli_success,
    cli_warning,
    cli_error,
    cli_highlight,
    cli_network,
)

cli_info("Initializing simulation network...")
cli_network("Network topology loaded: Small-World (N=50, k=4).")
cli_success("Integration complete across all 100 timesteps.")
cli_warning("Nyquist limit triggered: effective omega capped.")
cli_error("Validation error: Adjacency matrix must be symmetric.")
```

---

## Implementation Reference (`src/kuramoto/cli/style.py`)

A minimal, zero-dependency Click + ANSI truecolor implementation:

```python
"""
src/kuramoto/cli/style.py — Semantic CLI output styling.
"""
from __future__ import annotations

import click

# Semantic Click color mappings
STYLE_MAP = {
    "info": "bright_cyan",
    "network": "bright_magenta",
    "success": "bright_green",
    "warning": "bright_yellow",
    "error": "bright_red",
    "highlight": "bright_magenta",
}

def cli_message(msg: str, level: str = "info", bold: bool = False) -> None:
    """Print a styled message using the semantic color palette."""
    fg = STYLE_MAP.get(level, "bright_cyan")
    click.secho(msg, fg=fg, bold=bold)

def cli_info(msg: str) -> None:
    """Print an informational prompt (Electric Cyan)."""
    cli_message(f"ℹ️ {msg}", level="info")

def cli_network(msg: str) -> None:
    """Print a topology or structural update (Secondary Violet)."""
    cli_message(f"🌐 {msg}", level="network", bold=True)

def cli_success(msg: str) -> None:
    """Print a success confirmation (Tertiary Green)."""
    cli_message(f"✅ {msg}", level="success", bold=True)

def cli_warning(msg: str) -> None:
    """Print a warning notification (Quaternary Amber)."""
    cli_message(f"⚠️ {msg}", level="warning")

def cli_error(msg: str) -> None:
    """Print an error alert (Pernary Red/Magenta)."""
    cli_message(f"❌ {msg}", level="error", bold=True)
```

---

## Migration Plan

When implementing CLI commands or updating existing subcommands (`kuramoto/cli/`):
1. Replace direct `click.secho(..., fg="green")` calls with `cli_success(...)`.
2. Replace direct `click.secho(..., fg="yellow")` calls with `cli_warning(...)`.
3. Replace direct `click.secho(..., fg="red")` calls with `cli_error(...)`.
4. Replace direct `click.secho(..., fg="blue")` or `fg="cyan"` calls with `cli_info(...)`.
5. Use `cli_network(...)` for graph / topology generation commands (`kuramoto network`, `kuramoto generate`).

---

## Status

**Ready for implementation.** The specification is aligned with `.scriber-core/.junie/AGENTS.md` and ready for integration into `src/kuramoto/cli/style.py`.