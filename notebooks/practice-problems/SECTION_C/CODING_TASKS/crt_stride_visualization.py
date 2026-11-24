# notebooks/practice-problems/SECTION_c/CODING_TASKS/crt_stride_visualization.py
"""
crt_stride_visualization.py

CRT coprime-stride visualization module for the Kuramoto benchmark suite: diagnostic-first figures wrapped around a
memory-saving snapshot  mechanism, rendered with the scriber-core color palette.

What each figure answers
------------------------
figure1(): "Is my sampling correct? Does my solver drift? Where?"
    Panel 1 - CRT hit-map: a 7x11 grid where cell (a, b) is colored by the unique time step t in [0, 77) with
    t = a (mod 7), t = b (mod 11).
    The Chinese Remainder Theorem guarantees this is a bijection, so the pattern must be a perfectly regular
    permutation; irregularity means broken stride logic.
    Panel 2 - Residual heatmaps (healthy vs. drifted): phases recorded only at coprime strides, linearly reconstructed,
    scored per CRT cell against truth. Warm colors growing between strides = drift.
    Panel 3 - Phase hue shear: cyclic hue encoding of reconstructed phase; smooth winding = healthy, hue shear across
    CRT bands = frequency drift.

crt_trace_figure(k_m, k_n, M, N): the algebra-geometry bridge.
    Visual mirror of trace_crt_reconstruction(): Step 1 (Bezout) becomes the guarantee that the highlighted row and
    column meet exactly once; Step 2 sweeps column k_n in channel-A blue; Step 3 sweeps row k_m in channel-B violet;
    Step 4 lights the intersection gold with k_true; Step 5 verifies the cell coordinates against the remainder pair.
    Consumes kuramoto.solvers.coprime primitives when importable, so figure and CLI trace print identical numbers by
    construction.

crt_noncoprime_figure(k_m, k_n, M, N): the cautionary tale.
    Visual mirror of trace_crt_reconstruction_error(): with gcd = g > 1, unreachable cells form black dead-zone stripes
    (a = b mod g required), a consistent remainder pair collides on g crimson cells, and an inconsistent pair crosses
    a dead zone.

Author: Eigenscribe
Review status: Draft -- awaiting benchmark-suite integration review.
Date: November 24, 2026
"""

from __future__ import annotations

from typing import Callable, Final, TypeAlias

import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from scriber_core.frontend.colors import COLOR_PALETTE, hex_to_rgb

# -----------------------------------------------------------------------------------------------------------
# 🎭 Typing helpers / protocols / constants (define once, use Final)
# -----------------------------------------------------------------------------------------------------------

RGB01: TypeAlias = tuple[float, float, float]
HexColor: TypeAlias = str

# Canonical coprime strides (structural dimensions of the diagnostic)
M: Final[int] = 7
N: Final[int] = 11
TOTAL: Final[int] = M * N  # 77 - the coprime period

# Toy rotor constant, deliberately non-aligned with either stride
OMEGA: Final[float] = 2.0 * np.pi / 17.0

# Drift magnitudes for the healthy vs. drifted comparison panels
HEALTHY_DRIFT: Final[float] = 0.0
DRIFTED_DRIFT: Final[float] = 0.002

# Output filenames (figure art only, never embed personal data here)
FIGURE1_PATH: Final[str] = "crt_stride_diagnostics.png"
TRACE_FIGURE_PATH: Final[str] = "crt_trace_figure.png"
NONCOPRIME_FIGURE_PATH: Final[str] = "crt_noncoprime_stride_diagnostics.png"

# PaletteLoader protocol - dependency injection of colors.py
PaletteLoader: TypeAlias = Callable[[list[HexColor], int], list[RGB01]]

# Semantic color roles
CALM: Final[HexColor] = COLOR_PALETTE["reef_cyan"]
WARN: Final[HexColor] = COLOR_PALETTE["warning_amber"]
ALERT: Final[HexColor] = COLOR_PALETTE["error_crimson"]
INK: Final[HexColor] = COLOR_PALETTE["ibm_black"]
DIM_GRAY: Final[HexColor] = COLOR_PALETTE["ibm_gray"]
ICE_TEXT: Final[HexColor] = COLOR_PALETTE["ice_blue"]
CHAN_A: Final[HexColor] = COLOR_PALETTE["hot_pink"]
CHAN_B: Final[HexColor] = COLOR_PALETTE["eigen_blue"]
MERGE_GOLD: Final[HexColor] = COLOR_PALETTE["golden_amber"]
HITMAP_STOPS: Final[tuple[HexColor, ...]] = (
    COLOR_PALETTE["midnight_navy"],
    COLOR_PALETTE["eigen_blue"],
    COLOR_PALETTE["cosmic_iris"],
    COLOR_PALETTE["reef_cyan"],
    COLOR_PALETTE["vivid_pink"]
)


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core definitions (what exists)
#
# The CRT machinery: stride grids, snapshot bookkeeping, toy rotor physics,
# and the color engine wiring. Figures never contain raw CRT math directly.
# -----------------------------------------------------------------------------------------------------------


def hex_to_rgb01(hex_color: str) -> RGB01:
    """Normalize a six-digit hex color to an (R, G, B) tuple in [0, 1].

    Delegates to `hex_to_rgb` from scriber_core.frontend.colors and divides
    each channel by 255.0 to produce unit-range floats suitable for
    matplotlib color triples.

    Parameters
    ----------
    hex_color : str
        Six-digit hexadecimal color string, with or without leading '#'.

    Returns
    -------
    RGB01
        Three floats in [0, 1].

    Raises
    ------
    ValueError
        If hex_color is not a valid 6-digit hexadecimal color string.
    """
    r, g, b = hex_to_rgb(hex_color)
    return (r / 255.0, g / 255.0, b / 255.0)


def load_palette_engine() -> tuple[PaletteLoader, bool]:
    """Wire the color engine to colors.py in the scriber-core package when available.

    Prefers the eigenscribe golden-ratio gradient engine (golden easing across color transitions);
    falls back to plain linear interpolation through the same stops so the module is standalone importable.

    Returns
    -------
    tuple[PaletteLoader, bool]
        The loader callable and a flag telling whether the project engine was successfully imported (surfaced by smoke
        tests and figures).
    """
    try:
        import scriber_core.frontend.colors as cs

        def golden_loader(stops: list[HexColor], n: int) -> list[RGB01]:
            rgb255 = cs.generate_golden_ratio_gradient(stops, length=n)
            return [(r / 255.0, g / 255.0, b / 255.0) for r, g, b in rgb255]

        return golden_loader, True
    except ImportError:

        def linear_loader(stops: list[HexColor], n: int) -> list[RGB01]:
            rgbs = [hex_to_rgb01(s) for s in stops]
            segments = len(rgbs) - 1
            samples: list[RGB01] = []
            for i in range(n):
                progress = i / (n - 1) * segments
                seg = min(int(progress), segments - 1)
                frac = progress - seg
                samples.append(
                    tuple(
                        rgbs[seg][c] + (rgbs[seg + 1][c] - rgbs[seg][c]) * frac
                        for c in range(3)
                    )
                )
            return samples

        return linear_loader, False

PALETTE_LOADER: Final[PaletteLoader]
USING_PROJECT_COLORS: Final[bool] = True
PALETTE_LOADER, USING_PROJECT_COLORS = load_palette_engine()

def residual_colormap() -> LinearSegmentedColormap:
    """Build the calm -> warn -> alert colormap for residual panels.

    Uses reef_cyan, warning_amber, and error_crimson stops, eased by the golden-ratio engine when colors.py is
    importable.

    Returns
    -------
    LinearSegmentedColormap
        Colormap encoding reconstruction fidelity per CRT cell.
    """
    grad = PALETTE_LOADER([CALM, WARN, ALERT], 256)
    return LinearSegmentedColormap.from_list("crt_residual", grad)

def crt_cell_to_step(a: int, b: int, m: int, n: int) -> int:
    """Resolve the unique t in [0, m*n) for a remainder pair (a mod m, b mod n).

    Uses the same Bezout coefficients as the CLI trace: with (g, bez_a, bez_b) = extended_gcd(m, n) and
    bez_a*m + bez_b*n = 1, the merged reconstruction is t = bez_a*m*b + bez_b*n*a (mod m*n). Identical arithmetic to
    Steps 2-4 of trace_crt_reconstruction().

    Parameters
    ----------
    a : int
        Row residue, corresponding to the observed alias k_m mod m.
    b : int
        Column residue, corresponding to the observed alias k_n mod n.
    m : int
        First stride (coprime to n for a unique answer).
    n : int
        Second stride (coprime to m for a unique answer).

    Returns
    -------
    int
        The unique time step in [0, m*n) satisfying both congruences.

    Raises
    ------
    ValueError
        If the strides are not coprime - reconstruction is then ambiguous.
    """
    g, bez_a, bez_b = _local_extended_gcd(m, n)
    if g != 1:
        raise ValueError(f"crt_cell_to_step requires coprime strides; gcd{m},{n}={g}")
    return (bez_a * m * b + bez_b * n * a) % (m * n)

def build_step_grid(m: int = M, n: int = N) -> NDArray[np.int64]:
    """Build the CRT hit-map grid for coprime strides.

    Parameters
    ----------
    m : int, default=M
        Row stride.
    n : int, default=N
        Column stride.

    Returns
    -------
    NDArray[np.int64]
        Shape (m, n); entry (a, b) is the unique time step that CRT cell represents. For coprime strides this is a
        permutation of range (m*n).
    """
    return np.array(
        [[crt_cell_to_step(a, b, m, n) for b in range(n)] for a in range(m)],
        dtype=np.int64,
    )

def coprime_snapshot_steps(m: int = M, n: int = N) -> tuple[list[int], list[int], list[int]]:
    """Enumerate the steps recorded by each channel and their sorted union.

    Channel A records every m-th step, channel B every n-th step; both include the boundary step m*n. Memory: len(union)
    snapshots instead of dense m*n + 1.

    Parameters
    ----------
    m : int, default=M
        Channel A stride.
    n : int, default=N
        Channel B stride.

    Returns
    -------
    tuple[list[int], list[int], list[int]]
        Channel A steps, channel B steps, and their sorted union.
    """
    chan_a = list(range(0, m * n + 1, m))
    chan_b = list(range(0, m * n + 1, n))
    union = sorted(set(chan_a) | set(chan_b))
    return chan_a, chan_b, union
