# viz.py Refactoring Plan

## Why this matters

`src/kuramoto/analysis/viz.py` is a single 1,791-line monolithic file that mixes design tokens, colormap factories, plotting functions, font management, and private helpers in one module. This makes it difficult to:

- Navigate and modify individual components without risking unrelated breakage.
- Reason about dependencies — constants leak into plot functions and vice versa.
- Apply the project's own `HOUSE_RULES.md` guidance on modular design.
- Iterate on styling independently from plotting logic.

Splitting this file into focused submodules improves maintainability, enables targeted testing, and aligns with the project's "Gold Standard" module pattern.

---

## Current state

The file is organized (via emoji section dividers) into three rough sections:

| Section | Lines | Content |
|---|---|---|
| `0️⃣ Definitions, Constants & Design Tokens` | 37–314 | Theme colors, `PROJECT_COLORS`, `SOLVER_COLORS`, `COMPARISON_PALETTE`, golden ratio constants, 8 semantic `LinearSegmentedColormap` instances, gradient dictionaries, and backwards-compat aliases |
| `1️⃣ Public API` | 319–1341 | `set_style()`, `get_colormap()`, `get_comparison_colors()`, `get_node_colors()`, and 12 plotting functions (`plot_network`, `plot_distributions`, `plot_order_parameter`, `plot_autocorrelation`, `plot_fluid_vorticity`, `plot_time_series`, `plot_fourier_variability`, `plot_fourier_convergence`, `plot_psd_variability`, `plot_psd_convergence`, `plot_semantic_colormaps`) |
| `2️⃣ Internal Logic & Helpers` | 1344–1703 | `_apply_aclonica_font()`, `_plot_gradient_bar()`, `_add_parameter_row()`, `_add_spike_lines()`, `detect_transition_spikes()` |
| `💨 Smoke Tests` | 1713–1776 | `_run_smoke_test()` |
| `🔥 Entry Point` | 1782–1790 | `main()` |

### External consumers

Only two files import directly from `kuramoto.analysis.viz`:

| File | Imports |
|---|---|
| `scripts/rigorous_benchmarks.py` | `set_style`, `SOLVER_COLORS`, `PROJECT_COLORS` |
| `scripts/viz_3d_sync.py` | `set_style`, `PROJECT_COLORS` |

No code in `src/kuramoto/cli/` imports from `viz` — the CLI uses `click` and `tabulate` for output.

The `kuramoto/analysis/__init__.py` is currently empty — no package-level re-exports exist.

---

## Design principles

- **Preserve all existing imports.** Any code that currently does `from kuramoto.analysis.viz import X` must continue to work without changes.
- **Separate concerns cleanly.** Design tokens, colormaps, plot functions, and helpers each get their own module.
- **Follow the Gold Standard pattern.** Each new submodule should have `0️⃣` constants, `1️⃣` public API, `2️⃣` internal helpers, `💨` smoke tests, and `🔥` entry point.
- **Keep the `viz.py` file as a re-export hub.** Rather than deleting it, convert it to a thin barrel file that re-exports everything from the submodules.
- **Populate `analysis/__init__.py`.** Add explicit `__all__` exports per `HOUSE_RULES.md` Rule 6.
- **No new dependencies.** The refactor uses only `matplotlib`, `seaborn`, `numpy`, and `networkx` — already installed.

---

## Proposed module structure

```
src/kuramoto/analysis/
├── __init__.py              # Explicit __all__ with curated public exports
├── viz.py                   # Thin re-export hub (backward compat)
├── viz/
│   ├── __init__.py          # Re-exports from all submodules
│   ├── theme.py             # Design tokens, colors, fonts, set_style()
│   ├── colormaps.py         # Semantic colormaps, gradient dicts, get_colormap()
│   ├── plots.py             # All plot_* public functions
│   └── helpers.py           # Private helpers and detect_transition_spikes()
```

### Module responsibilities

#### `viz/theme.py` — Design Tokens & Styling

**Moves from `viz.py` lines ~37–168 and `set_style()` (~319–389)**

| Category | Symbols |
|---|---|
| Core design tokens | `THEME_BG`, `CARD_BG`, `BORDER_COLOR`, `GRID_COLOR`, `TEXT_PRIMARY`, `TEXT_MUTED` |
| Color palettes | `PROJECT_COLORS`, `SCRIBER_PALETTE`, `SOLVER_COLORS`, `COMPARISON_PALETTE` |
| Color constants | `COLOR_RK45`, `COLOR_EULER`, `COLOR_ROTOR`, `COLOR_GROUND_TRUTH`, `COLOR_REFERENCE`, `COLOR_SIMULATED`, `COLOR_TRUE`, `COLOR_LEARNED`, `COLOR_OBSERVED` |
| Golden ratio | `GOLDEN_RATIO`, `PHI`, `INV_PHI`, `INV_PHI2`, `INV_PHI3`, `INV_PHI4` |
| Font setup | Aclonica font detection loop (lines 42–53) |
| Public function | `set_style()` |

#### `viz/colormaps.py` — Colormap Factories

**Moves from `viz.py` lines ~172–314 and `get_colormap()` (~393–425)**

| Category | Symbols |
|---|---|
| Colormap instances | `phase_cmap`, `order_parameter_cmap`, `spectral_density_cmap`, `hamiltonian_cmap`, `spatial_overlap_cmap`, `temporal_overlap_cmap`, `cross_overlap_cmap`, `temporal_cmap` |
| Uppercase aliases | `PHASE_CMAP`, `ORDER_PARAMETER_CMAP`, `SPECTRAL_DENSITY_CMAP`, `HAMILTONIAN_CMAP`, `SPATIAL_OVERLAP_CMAP`, `TEMPORAL_OVERLAP_CMAP`, `CROSS_OVERLAP_CMAP`, `TEMPORAL_CMAP`, `BLUE_TO_PINK` |
| Backwards-compat aliases | `TEMPORAL_POD_CMAP`, `SPATIAL_POD_CMAP`, `WAVEFUNCTION_CMAP`, `WAVEFUNCTION_OVERLAP_CMAP`, `HAMILTONIAN_DENSITY_CMAP`, `temporal_pod_cmap`, `spatial_pod_cmap`, `wavefunction_cmap`, `wavefunction_overlap_cmap`, `hamiltonian_density_cmap` |
| Gradient dicts | `GRADIENTS` |
| Public function | `get_colormap(name)` |

#### `viz/plots.py` — Plotting Functions

**Moves from `viz.py` lines ~427–1341**

| Function | Description |
|---|---|
| `get_comparison_colors(quantity)` | Returns reference/simulated color pair |
| `get_node_colors(adjacency, values, ...)` | Computes node colors from adjacency matrix |
| `plot_network(adjacency, ...)` | Network graph visualization |
| `plot_distributions(omega, theta_0, ...)` | Frequency and phase distribution plots |
| `plot_order_parameter(times, r_values, ...)` | Order parameter time series |
| `plot_autocorrelation(series, ...)` | Autocorrelation plot |
| `plot_fluid_vorticity(phases, omega, ...)` | Phase velocity field visualization |
| `plot_time_series(times, theta, ...)` | Phase time series |
| `plot_fourier_variability(amplitudes, ...)` | Fourier amplitude bar chart |
| `plot_fourier_convergence(durations, amplitudes, ...)` | Fourier convergence line plot |
| `plot_psd_variability(frequencies, psd_values, ...)` | PSD line plot with target marker |
| `plot_psd_convergence(frequencies, psd_data, ...)` | Multi-window PSD convergence |
| `plot_semantic_colormaps(out_path)` | Renders all semantic colormaps |

#### `viz/helpers.py` — Private Helpers

**Moves from `viz.py` lines ~1344–1703**

| Function | Description |
|---|---|
| `_apply_aclonica_font(ax)` | Applies Aclonica font to axes elements |
| `_plot_gradient_bar(ax, ...)` | Draws gradient-filled bar segments |
| `_add_parameter_row(fig, parameters, ...)` | Renders parameter badge overlay |
| `_add_spike_lines(ax, spike_epochs, ...)` | Draws vertical transition indicators |
| `detect_transition_spikes(epochs, series, ...)` | Detects gradient spikes in time series |
| `detect_loss_spikes` | Backwards-compat alias for `detect_transition_spikes` |
| `_add_lambda_row` | Backwards-compat alias for `_add_parameter_row` |

---

## Implementation phases

### Phase 1: Create submodules and move code

1. Create `src/kuramoto/analysis/viz/` package directory with `__init__.py`.
2. Create `theme.py` — move all design tokens, color constants, font detection, and `set_style()`.
3. Create `colormaps.py` — move all colormap instances, gradient dicts, and `get_colormap()`.
4. Create `plots.py` — move all `plot_*` functions and `get_comparison_colors()`, `get_node_colors()`.
5. Create `helpers.py` — move all private `_` helpers and `detect_transition_spikes()`.
6. Each submodule imports only what it needs from sibling modules (e.g., `plots.py` imports `set_style` from `theme.py` and colormap constants from `colormaps.py`).

### Phase 2: Convert `viz.py` to a re-export hub

Replace the body of `viz.py` with a thin barrel file:

```python
"""
viz.py — Backward-compatible re-export hub.

All symbols are now defined in kuramoto.analysis.viz.* submodules.
This file re-exports them so that existing import paths continue to work.
"""
from __future__ import annotations

# Theme tokens
from kuramoto.analysis.viz.theme import (
    THEME_BG,
    CARD_BG,
    BORDER_COLOR,
    GRID_COLOR,
    TEXT_PRIMARY,
    TEXT_MUTED,
    PROJECT_COLORS,
    SCRIBER_PALETTE,
    SOLVER_COLORS,
    COMPARISON_PALETTE,
    COLOR_RK45,
    COLOR_EULER,
    COLOR_ROTOR,
    COLOR_GROUND_TRUTH,
    COLOR_REFERENCE,
    COLOR_SIMULATED,
    COLOR_TRUE,
    COLOR_LEARNED,
    COLOR_OBSERVED,
    GOLDEN_RATIO,
    PHI,
    INV_PHI,
    INV_PHI2,
    INV_PHI3,
    INV_PHI4,
    set_style,
)

# Colormaps
from kuramoto.analysis.viz.colormaps import (
    phase_cmap,
    order_parameter_cmap,
    spectral_density_cmap,
    hamiltonian_cmap,
    spatial_overlap_cmap,
    temporal_overlap_cmap,
    cross_overlap_cmap,
    temporal_cmap,
    PHASE_CMAP,
    ORDER_PARAMETER_CMAP,
    SPECTRAL_DENSITY_CMAP,
    HAMILTONIAN_CMAP,
    SPATIAL_OVERLAP_CMAP,
    TEMPORAL_OVERLAP_CMAP,
    CROSS_OVERLAP_CMAP,
    TEMPORAL_CMAP,
    BLUE_TO_PINK,
    GRADIENTS,
    get_colormap,
    # Backwards-compat aliases
    TEMPORAL_POD_CMAP,
    SPATIAL_POD_CMAP,
    WAVEFUNCTION_CMAP,
    WAVEFUNCTION_OVERLAP_CMAP,
    HAMILTONIAN_DENSITY_CMAP,
    temporal_pod_cmap,
    spatial_pod_cmap,
    wavefunction_cmap,
    wavefunction_overlap_cmap,
    hamiltonian_density_cmap,
)

# Plot functions
from kuramoto.analysis.viz.plots import (
    get_comparison_colors,
    get_node_colors,
    plot_network,
    plot_distributions,
    plot_order_parameter,
    plot_autocorrelation,
    plot_fluid_vorticity,
    plot_time_series,
    plot_fourier_variability,
    plot_fourier_convergence,
    plot_psd_variability,
    plot_psd_convergence,
    plot_semantic_colormaps,
)

# Helpers
from kuramoto.analysis.viz.helpers import (
    _apply_aclonica_font,
    _plot_gradient_bar,
    _add_parameter_row,
    _add_spike_lines,
    detect_transition_spikes,
    detect_loss_spikes,
    _add_lambda_row,
)

# Smoke test and entry point
from kuramoto.analysis.viz import _run_smoke_test, main  # type: ignore

__all__ = [
    # Theme
    "THEME_BG", "CARD_BG", "BORDER_COLOR", "GRID_COLOR",
    "TEXT_PRIMARY", "TEXT_MUTED",
    "PROJECT_COLORS", "SCRIBER_PALETTE", "SOLVER_COLORS", "COMPARISON_PALETTE",
    "COLOR_RK45", "COLOR_EULER", "COLOR_ROTOR", "COLOR_GROUND_TRUTH",
    "COLOR_REFERENCE", "COLOR_SIMULATED",
    "COLOR_TRUE", "COLOR_LEARNED", "COLOR_OBSERVED",
    "GOLDEN_RATIO", "PHI", "INV_PHI", "INV_PHI2", "INV_PHI3", "INV_PHI4",
    "set_style",
    # Colormaps
    "phase_cmap", "order_parameter_cmap", "spectral_density_cmap",
    "hamiltonian_cmap", "spatial_overlap_cmap", "temporal_overlap_cmap",
    "cross_overlap_cmap", "temporal_cmap",
    "PHASE_CMAP", "ORDER_PARAMETER_CMAP", "SPECTRAL_DENSITY_CMAP",
    "HAMILTONIAN_CMAP", "SPATIAL_OVERLAP_CMAP", "TEMPORAL_OVERLAP_CMAP",
    "CROSS_OVERLAP_CMAP", "TEMPORAL_CMAP", "BLUE_TO_PINK",
    "GRADIENTS", "get_colormap",
    # Plots
    "get_comparison_colors", "get_node_colors",
    "plot_network", "plot_distributions", "plot_order_parameter",
    "plot_autocorrelation", "plot_fluid_vorticity", "plot_time_series",
    "plot_fourier_variability", "plot_fourier_convergence",
    "plot_psd_variability", "plot_psd_convergence", "plot_semantic_colormaps",
    # Helpers
    "_apply_aclonica_font", "_plot_gradient_bar", "_add_parameter_row",
    "_add_spike_lines", "detect_transition_spikes",
    "detect_loss_spikes", "_add_lambda_row",
    # Entry
    "_run_smoke_test", "main",
]
```

### Phase 3: Populate `analysis/__init__.py`

Add explicit `__all__` to `kuramoto/analysis/__init__.py` per `HOUSE_RULES.md` Rule 6:

```python
"""Analysis subpackage — spectral diagnostics and visualization."""
from __future__ import annotations

from kuramoto.analysis.spectral import (
    compute_fourier_coefficients,
    compute_psd,
    spectral_decomposition,
)
from kuramoto.analysis.viz import set_style, plot_order_parameter, plot_time_series

__all__ = [
    "compute_fourier_coefficients",
    "compute_psd",
    "spectral_decomposition",
    "set_style",
    "plot_order_parameter",
    "plot_time_series",
]
```

### Phase 4: Verify backward compatibility

1. Run existing tests: `uv run pytest tests/ -v`
2. Run the smoke test: `uv run python -m kuramoto.analysis.viz`
3. Verify external scripts still work:
   - `scripts/rigorous_benchmarks.py` — imports `set_style`, `SOLVER_COLORS`, `PROJECT_COLORS`
   - `scripts/viz_3d_sync.py` — imports `set_style`, `PROJECT_COLORS`
4. Confirm no circular imports by importing the package fresh:
   ```python
   python -c "from kuramoto.analysis.viz import set_style, plot_network, PHASE_CMAP; print('OK')"
   ```

---

## Backward compatibility strategy

The key insight is that **`viz.py` is not deleted** — it becomes a thin re-export barrel. This means:

- `from kuramoto.analysis.viz import set_style` → Still works
- `from kuramoto.analysis.viz import PROJECT_COLORS` → Still works
- `from kuramoto.analysis.viz import plot_network` → Still works
- `from kuramoto.analysis.viz import _apply_aclonica_font` → Still works (private, but preserved)

New code can import directly from submodules for clarity:

```python
from kuramoto.analysis.viz.theme import set_style, PROJECT_COLORS
from kuramoto.analysis.viz.colormaps import PHASE_CMAP, get_colormap
from kuramoto.analysis.viz.plots import plot_network, plot_order_parameter
```

---

## File size estimates after split

| Module | Estimated lines |
|---|---|
| `viz.py` (re-export hub) | ~90 |
| `viz/__init__.py` | ~10 |
| `viz/theme.py` | ~180 |
| `viz/colormaps.py` | ~130 |
| `viz/plots.py` | ~1,050 |
| `viz/helpers.py` | ~340 |
| **Total** | **~1,800** (same content, better organized) |

The largest remaining file is `plots.py` (~1,050 lines), which is acceptable because each plot function is self-contained and independently testable. Further splitting of `plots.py` into individual plot modules is not recommended at this time — it would create excessive fragmentation for functions that are already well-encapsulated.

---

## Potential pitfalls

1. **Circular imports**: `plots.py` imports from `theme.py` and `colormaps.py`. Ensure no submodule imports back from `plots.py` or the re-export `viz.py`.
2. **`__name__ == "__main__"` in `viz.py`**: The smoke test and `main()` entry point need to remain in a location where `python -m kuramoto.analysis.viz` still works. Consider placing them in `viz/__init__.py` or keeping a minimal stub in `viz.py`.
3. **Backwards-compat aliases**: There are many alias constants (e.g., `detect_loss_spikes`, `_add_lambda_row`, `TEMPORAL_POD_CMAP`). All must be re-exported to avoid silent breakage.
4. **`GRADIENTS` dict**: Used by both `get_colormap()` and several plot functions. Must be accessible from both `colormaps.py` and `plots.py`.

---

## Related cleanup opportunities

Once the split is complete, consider:

- **Adding per-plot smoke tests**: Each `plot_*` function could have a minimal test in `tests/test_viz_plots.py` verifying it produces a figure without error.
- **Dark theme as default**: `set_style()` could be called automatically in `__init__.py` to avoid requiring callers to invoke it manually.
- **Light theme support**: Add a `set_style(theme="light")` variant for publications or presentations requiring light backgrounds.
- **Seaborn integration**: Evaluate whether `sns.set_theme()` can replace or complement the manual `plt.rcParams` calls in `set_style()`.

---

## Status

**Parked for later.** This is a nontrivial refactoring requiring careful attention to backward compatibility. Do not pursue during unrelated debugging or feature work unless visualization module maintenance is the explicit task.

Estimated effort: 2–3 hours for an experienced contributor familiar with the codebase.
