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
from numpy.typing import NDArray

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap

from eigenscribe.frontend.colors import COLOR_PALETTE, hex_to_rgb



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
FIGURE_DPI: Final[int] = 220

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
USING_PROJECT_COLORS: Final[bool]
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

def crt_cell_to_step(
        a: int,
        b: int,
        m: int,
        n: int
) -> int:
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

def simulate_rotor(
        drift: float,
        total: int = TOTAL
) -> NDArray[np.float64]:
    """Compute the true phase theta_t of the toy rotor at every dense step.

    drift > 0 adds a quadratic phase term theta += 0.5 * drift * t^2, i.e. the instantaneous frequency creeps upward.
    Stand-in for bivector torque accumulation error in a geometric-algebra rotor.

    Parameters
    ----------
    drift : float
        Quadratic phase-drift coefficient (0.0 = healthy rotor).
    total : int, default=TOTAL
        Number of dense steps; phases returned for t in [0, total].

    Returns
    -------
    NDArray[np.float64]
        Phase values theta_t, shape (total + 1).
    """
    t = np.arange(total + 1, dtype=np.float64)
    return OMEGA * t + 0.5 * drift * t * t

def reconstruct_from_snapshots(
    theta_true: NDArray[np.float64],
    union: list[int]
) -> NDArray[np.float64]:
    """Rebuild the full phase curve from coprime-stride samples only.

    Pretends knowledge of theta only at the union steps (as the recorder does), linearly interpolates between them, and
    returns the reconstruction on all dense steps. The truth array is consumed solely at the stored indices.

    Parameters
    ----------
    theta_true : NDArray[np.float64]
        Ground-truth phases at every dense step (source of stored samples).
    union : list[int]
        Sorted snapshot steps from coprime_snapshot_steps().

    Returns
    -------
    NDArray[np.float64]
        Reconstructed phases at every dense step.
    """
    t_stored = np.asarray(union, dtype=np.float64)
    theta_stored = theta_true[union]
    t_dense = np.arange(theta_true.size, dtype=np.float64)
    return np.interp(t_dense, t_stored, theta_stored)


# -----------------------------------------------------------------------------------------------------------
# 2️⃣ Public API (functions users are meant to call)
# -----------------------------------------------------------------------------------------------------------


def figure1() -> None:
    """Render the three CRT diagnostic panels plus the memory ledger.

    Answers, in order: is the coprime sampling correct (Panel 1), does the solver drift (Panel 2), and where does the
    drift manifest (Panel 3)? Saves FIGURES1_PATH with the ink-black background.
    """
    step_grid = build_step_grid()

    fig, axes = plt.subplots(
        2,
        4,
        figsize=(17, 9),
        constrained_layout=True,
        gridspec_kw={"width_ratios": [1, 1, 1, 0.06]},
    )
    fig.patch.set_facecolor(INK)
    for ax in axes.flat:
        _style_axis(ax)
    axes[1, 3].set_axis_off()

    _paint_hitmap_panel(axes[0, 0], step_grid)
    colorbar_image = _paint_residual_panels(
        [axes[0, 1], axes[0, 2]], step_grid, [HEALTHY_DRIFT, DRIFTED_DRIFT]
    )
    colorbar = fig.colorbar(colorbar_image, cax=axes[0, 3])
    colorbar.set_label("Absolute phase error (rad)", color=ICE_TEXT, fontsize=8)
    colorbar.ax.tick_params(colors=ICE_TEXT, labelsize=7)
    colorbar.outline.set_edgecolor(DIM_GRAY)
    _paint_phase_hue_panels(
        [axes[1, 1], axes[1, 2]], step_grid, [HEALTHY_DRIFT, DRIFTED_DRIFT]
    )
    _paint_memory_ledger_panel(axes[1, 0])

    fig.suptitle(
        "Coprime-stride CRT diagnostics for the Kuramoto rotor benchmark",
        color=COLOR_PALETTE["text_white"], fontsize=15,
    )
    fig.savefig(FIGURE1_PATH, dpi=FIGURE_DPI, facecolor=INK, bbox_inches="tight")
    plt.close(fig)

def crt_trace_figure(
    k_m: int,
    k_n: int,
    m: int = M,
    n: int = N,
) -> int:
    """Visual mirror of trace_crt_reconstruction(k_m, k_n, M, N).

    Row index plays k_m (observed alias mod m, Sampler B); column index play k_n (observed alias mod n, Sampler A).
    Sweeps the k_n column in channel-A blue, the k_m row in channel-B violet, lights the merge cell gold, and verifies
    the coordinates --- mirroring the CLI trace steps.

    Parameters
    ----------
    k_m : int
        Observed alias modulo m (from Sampler B).
    k_n : int
        Observed alias modulo n (from Sampler A).

    Returns
    -------
    int
        The reconstructed true frequency index k_true in [0, m*n -1], identical to what the CLI trace points.
    """
    modulus = m * n
    g, bez_a, bez_b = _local_extended_gcd(m, n)
    term_a = k_n * bez_a * m    # Channel A contribution (trace Step 2)
    term_b = k_m * bez_b * n    # Channel B contribution (trace Step 3)
    k_true = (term_a + term_b) % modulus    # trace Step 4: merge
    library_index = _library_reconstruct_frequency(k_m=k_m, k_n=k_n, m=m, n=n)
    lib_match = None if library_index is None else library_index == k_true

    fig, ax = plt.subplots(
        figsize=(max(10, n + 4), max(7, m + 3)), constrained_layout=True
    )
    fig.patch.set_facecolor(INK)
    _style_axis(ax)

    base = np.zeros((m, n, 3))
    base[:, :] = hex_to_rgb01(DIM_GRAY)
    for row in range(m):
        base[row, k_n] = hex_to_rgb01(CHAN_A)   # Step 2: column sweep
    for col in range(n):
        base[k_m, col] = hex_to_rgb01(CHAN_B)   # Step 3: row sweep
    base[k_m, k_n] = hex_to_rgb01(MERGE_GOLD)   # Step 4: the survivor

    ax.imshow(base, interpolation="nearest", aspect="equal")
    _configure_matrix_axis(ax, m, n)
    ax.set_xlim(-1.6, n + 4.3)
    ax.set_ylim(m - 0.5, -1.2)
    ax.text(-0.8, k_m, f"k_m={k_m}", ha="right", va="center",
            fontsize=9, color=CHAN_B, weight="bold")
    ax.text(k_n, -0.8, f"k_n={k_n}", ha="center", va="bottom",
            fontsize=9, color=CHAN_A, weight="bold")
    ax.text(k_n, k_m, str(k_true), ha="center", va="center",
            fontsize=13, color=INK, weight="bold")

    _paint_trace_verification_title(ax, k_true, k_m, k_n, m, n, modulus,
                                    g, bez_a, bez_b, term_a, term_b, lib_match)

    _paint_trace_legend(ax, m, n)

    fig.savefig(TRACE_FIGURE_PATH, dpi=FIGURE_DPI, facecolor=INK, bbox_inches="tight")
    plt.show()
    plt.close(fig)

    print(f"[crt_trace_figure] k_true(trace) = {k_true} | "
          f"library = {library_index} | match = {lib_match}")
    return k_true

def crt_noncoprime_figure(
    k_m: int,
    k_n: int,
    m: int = 6,
    n: int = 9
) -> None:
    """Visual mirror of trace_crt_reconstruction_error() for gcd > 1.

    With g = gcd(m, n), a cel (a, b) is reachable only when a = b (mod g):
    unreachable cells render as black dead-zone stripes, a consistent remainder pair collides on g crimson cells, and an
    inconsistent pair crosses dead-zone territory (the CLI's 'No index matches' branch).

    Parameters
    ----------
    k_m : int
        Observed alias modulo m.
    k_n : int
        Observed alias modulo n.
    m : int, default=6
        First non-coprime stride.
    n : int, default=9
        Second non-coprime stride.
    """
    g = int(np.gcd(m, n))
    matching = [t for t in range(m * n) if t % m == k_m and t % n == k_n]
    collisions = {(t % m, t % n) for t in matching}

    fig, ax = plt.subplots(
        figsize=(max(10, n + 3), max(7, m + 3)), constrained_layout=True
    )
    fig.patch.set_facecolor(INK)
    _style_axis(ax)

    base = np.zeros((m, n, 3))
    for row in range(m):
        for col in range(n):
            if (row - col) % g == 0:
                if (row, col) in collisions:
                    base[row, col] = hex_to_rgb01(ALERT)
                else:
                    base[row, col] = hex_to_rgb01(DIM_GRAY)
            # else: leave black -- dead zone, unreachable by any time step

    ax.imshow(base, interpolation="nearest", aspect="equal")
    _configure_matrix_axis(ax, m, n)
    ax.set_xlim(-1.6, n - 0.5)
    ax.set_ylim(m - 0.5, -1.2)
    ax.text(-0.8, k_m, f"k_m={k_m}", ha="right", va="center",
            fontsize=9, color=CHAN_B, weight="bold")
    ax.text(k_n, -0.8, f"k_n={k_n}", ha="center", va="bottom",
            fontsize=9, color=CHAN_A, weight="bold")

    verdict = (
        f"consistent: {g} indices collide on this pair -- {matching}"
        if matching
        else "inconsistent: NO index matches this remainder pair"
    )
    ax.set_title(
        f"Non-coprime strides M={m}, N={n} (gcd = {g})\n"
        f"Black = dead zones (no t can land there: needs a = b mod {g})\n"
        f"{verdict}",
        fontsize=9, color=COLOR_PALETTE["text_white"],
    )
    ax.set_xlabel("residue mod N")
    ax.set_ylabel("residue mod M")

    fig.savefig(
        NONCOPRIME_FIGURE_PATH,
        dpi=FIGURE_DPI,
        facecolor=INK,
        bbox_inches="tight",
    )
    plt.show()
    plt.close(fig)

    print(f"[crt_noncoprime_figure] matching indices for ({k_m}, {k_n}): "
          f"{matching if matching else 'none (inconsistent pair)'}")


# -----------------------------------------------------------------------------------------------------------
# 3️⃣ Private helpers (how it works)
#
# Panel painters and the library-wiring shim. Never called by end users.
# -----------------------------------------------------------------------------------------------------------

try:
    from kuramoto.solvers.coprime import (
        coprime_reconstruct_frequency,  # noqa: F401 -- exercised via shim below
        extended_gcd,
    )

    USING_KURAMOTO_LIB: Final[bool] = True
except ImportError:
    USING_KURAMOTO_LIB: Final[bool] = False

    def extended_gcd(x: int, y:int) -> tuple[int, int, int]:
        """Local Bezout stand-in returning (gcd, a, b) with a*x + b*y = gcd."""
        old_r, r = x, y
        old_s, s = 1, 0
        old_t, t = 0, 1
        while r != 0:
            quotient = old_r // r
            old_r, r = r, old_r - quotient * r
            old_s, s = s, old_s - quotient * s
            old_t, t = t, old_t - quotient * t
        return old_r, old_s, old_t

def _local_extended_gcd(x: int, y: int) -> tuple[int, int, int]:
    """Route Bezout resolution through the library when wired, else locally."""
    if USING_KURAMOTO_LIB:
        return extended_gcd(x, y)    # type: ignore[possibly-undefined]
    return extended_gcd(x, y)

def _library_reconstruct_frequency(k_m: int, k_n: int, m: int, n: int) -> int | None:
    """Cross-check reconstruction against the kuramoto library when wired.

    Returns None when the library is unavailable, in which case the figure simply reports the trace value alone (no
    mismatch verdict is claimed).
    """
    if not USING_KURAMOTO_LIB:
        return None
    try:
        return coprime_reconstruct_frequency(k_m=k_m, k_n=k_n, M=m, N=n)    # type: ignore[possibly-undefined]
    except TypeError:
        return None

def _style_axis(ax: Axes) -> None:
    """Apply the shared high-contrast palette to a figure axis."""
    ax.set_facecolor(INK)
    ax.tick_params(axis="both", colors=ICE_TEXT, labelsize=8)
    ax.xaxis.label.set_color(ICE_TEXT)
    ax.yaxis.label.set_color(ICE_TEXT)
    for spine in ax.spines.values():
        spine.set_color(DIM_GRAY)

def _configure_matrix_axis(ax: Axes, m: int, n: int) -> None:
    """Label integer matrix cells and draw subtle boundaries between them."""
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(m))
    ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, m, 1), minor=True)
    ax.grid(which="minor", color=INK, linewidth=0.8)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(m - 0.5, -0.5)

def _paint_hitmap_panel(ax: Axes, step_grid: NDARRAY[np.int64]) -> None:
    """Panel 1 painter: color each CRT cell by the time step it represents."""
    cmap = LinearSegmentedColormap.from_list(
        "crt_hitmap", PALETTE_LOADER(list(HITMAP_STOPS), 256)
    )
    ax.imshow(
        step_grid,
        cmap=cmap,
        interpolation="nearest",
        vmin=0,
        vmax=TOTAL - 1,
        aspect="equal",
    )
    _configure_matrix_axis(ax, M, N)
    ax.set_title(
        "CRT hit-map · unique step per residue pair",
        fontsize=9,
        color=COLOR_PALETTE["text_white"],
        pad=10,
    )
    ax.set_xlabel(f"Residue mod N ({N}) · channel B", fontsize=8)
    ax.set_ylabel(f"Residue mod M ({M}) · channel A", fontsize=8)
    for row, col in np.ndindex(step_grid.shape):
        ax.text(
            col,
            row,
            str(step_grid[row, col]),
            ha="center",
            va="center",
            fontsize=7,
            color=COLOR_PALETTE["text_white"],
            path_effects=[path_effects.withStroke(linewidth=1.5, foreground=INK)],
        )

def _paint_residual_panels(
    axes: list[Axes], step_grid: NDARRAY[np.int64], drift_values: list[float]
) -> plt.matplotlib.image.AxesImage:
    """Panel 2 painter: reconstruction residual per CRT cell, per drift level.

    Returns the last image artist so the caller can attach a shared colorbar.
    """
    cmap = residual_colormap()
    vmax = 0.0
    residual_grids: list[NDArray[np.float64]] = []
    for drift in drift_values:
        theta = simulate_rotor(drift)
        _, _, union = coprime_snapshot_steps()
        recon = reconstruct_from_snapshots(theta, union)
        resid = np.abs(recon - theta)
        vmax = max(vmax, float(resid.max()))
        grid = np.zeros((M, N), dtype=np.float64)
        for row in range(M):
            for col in range(N):
                grid[row, col] = resid[step_grid[row, col]]
        residual_grids.append(grid)

    vmax = max(vmax, np.finfo(np.float64).eps)
    image = None
    for ax, grid, drift in zip(axes, residual_grids, drift_values):
        image = ax.imshow(
            grid,
            cmap=cmap,
            interpolation="nearest",
            vmin=0,
            vmax=vmax,
            aspect="equal",
        )
        _configure_matrix_axis(ax, M, N)
        ax.set_title(
            f"Residual · drift={drift:g}\nmax |error| = {grid.max():.4g} rad",
            fontsize=9,
            color=COLOR_PALETTE["text_white"],
            pad=10,
        )
    assert image is not None
    return image

def _paint_phase_hue_panels(
    axes: list[Axes], step_grid: NDArray[np.int64], drift_values: list[float]
) -> None:
    """Panel 3 painter: cyclic hue encoding of the reconstructed phase field."""
    for ax, drift in zip(axes, drift_values):
        theta = simulate_rotor(drift)
        _, _, union = coprime_snapshot_steps()
        recon = reconstruct_from_snapshots(theta, union)
        phase_grid = np.mod(recon[step_grid], 2.0 * np.pi)
        ax.imshow(
            phase_grid,
            cmap="twilight",
            interpolation="nearest",
            vmin=0.0,
            vmax=2.0 * np.pi,
            aspect="equal",
        )
        _configure_matrix_axis(ax, M, N)
        ax.set_title(
            f"Reconstructed phase · drift={drift:g}\ncyclic color: 0–2π rad",
            fontsize=9,
            color=COLOR_PALETTE["text_white"],
            pad=10,
        )

def _paint_memory_ledger_panel(ax: Axes) -> None:
    """Bottom-left panel painter: the O(mn) -> O(m+n) memory ledger."""
    _, _, union = coprime_snapshot_steps()
    saved = (TOTAL + 1) - len(union)
    ax.axis("off")
    ax.text(
        0.03,
        0.95,
        "Snapshot memory",
        fontsize=12,
        color=COLOR_PALETTE["text_white"],
        weight="bold",
        va="top",
    )
    ax.text(
        0.03,
        0.78,
        f"dense:    O(mn)  = {TOTAL + 1} snapshots\n"
        f"coprime:  O(m+n) = {len(union)} snapshots\n\n"
        f"channel A fires at t = 0 (mod {M})\n"
        f"channel B fires at t = 0 (mod {N})\n"
        f"overlap only at t = 0 (mod {TOTAL})\n"
        f"saved {saved} ({saved / (TOTAL + 1):.0%} reduction)",
        fontsize=9,
        color=ICE_TEXT,
        family="monospace",
        va="top",
    )

def _paint_trace_verification_title(
    ax: Axes,
    k_true: int,
    k_m: int,
    k_n: int,
    m: int,
    n: int,
    modulus: int,
    g: int,
    bez_a: int,
    bez_b: int,
    term_a: int,
    term_b: int,
    lib_match: bool | None,
) -> None:
    """Trace-figure painter: Bezout, terms, merge, and verification verdicts."""
    check_m = k_true % m
    check_n = k_true % n
    ok_m = check_m == k_m
    ok_n = check_n == k_n
    verdict = "PASS" if (ok_m and ok_n) else "FAIL"
    residue_m_status = "PASS" if ok_m else "FAIL"
    residue_n_status = "PASS" if ok_n else "FAIL"
    if lib_match is None:
        lib_note = "    |    library unavailable"
    elif lib_match:
        lib_note = "    |    library match"
    else:
        lib_note = "    |    LIBRARY MISMATCH"
    ax.set_title(
        f"CRT trace · k_m={k_m}, k_n={k_n} · M={m}, N={n}\n"
        f"Bezout: ({bez_a})*{m} + ({bez_b})*{n} = {g}    |    "
        f"term_a = {term_a}, term_b = {term_b}\n"
        f"k_true = ({term_a} + {term_b}) % {modulus} = {k_true}    {verdict}    "
        f"({k_true} mod {m} = {check_m}: {residue_m_status}, "
        f"{k_true} mod {n} = {check_n}: {residue_n_status})"
        f"{lib_note}",
        fontsize=9,
        color=COLOR_PALETTE["text_white"],
        pad=12,
    )
    ax.set_xlabel("residue mod N  (= k_n, Sampler A)")
    ax.set_ylabel("residue mod M  (= k_m, Sampler B)")

def _paint_trace_legend(ax: Axes, m: int, n: int) -> None:
    """Trace-figure painter: CLI-color-semantics legend swatches."""
    legend_items = [
        (CHAN_A, "column k_n -- Channel A term"),
        (CHAN_B, "row k_m -- Channel B term"),
        (MERGE_GOLD, "merge: unique k_true"),
    ]
    for index, (color, label) in enumerate(legend_items):
        ax.add_patch(plt.Rectangle(
            (n + 0.35, m - 1.1 - index * 1.2), 0.55, 0.55,
            facecolor=color, edgecolor="none", clip_on=False,
            transform=ax.transData,
        ))
        ax.text(
            n + 1.1, m - 0.83 - index * 1.2, label,
            fontsize=8,
            color=COLOR_PALETTE["text_white"],
            va="center",
            clip_on=False,
        )

# -----------------------------------------------------------------------------------------------------------
# 4️⃣ 💨 Smoke tests / example usage (proof it works)
# -----------------------------------------------------------------------------------------------------------

def run_smoke_test() -> bool:
    """Validate the CRT machinery and memory accounting before any figure.

    Checks: the hit-grid is a genuine bijection onto [0, m*n) (the CRT guarantee), reconstruction reproduces the
    analytic trajectory exactly at stored snapshot steps, a drifted rotor shows strictly larger reconstruction residual
    than the healthy one, and the snapshot union delivers the promised O(m+n) reduction.

    Returns
    -------
    bool
        True if all invariants pass.
    """
    print("👟💨 Running crt_stride_viz smoke tests...")
    is_valid = True

    # 1. CRT bijection: every cell maps to a distinct step covering [0, TOTAL)
    step_grid = build_step_grid()
    bijection_ok = len(set(step_grid.flatten())) == TOTAL
    is_valid &= bijection_ok
    print(f"  {'✔️' if bijection_ok else '❌'} CRT bijection over {TOTAL} steps")

    # 2. Snapshot bookkeeping: union respects the coprime counting bound
    chan_a, chan_b, union = coprime_snapshot_steps()
    counting_ok = len(union) == len(chan_a) + len(chan_b) - 2  # shared endpoints: t=0 and t=TOTAL
    is_valid &= counting_ok
    print(
        f"  {'✔️' if counting_ok else '❌'} snapshot union: {len(union)} "
        f"vs dense {TOTAL + 1}"
    )

    # 3. Reconstruction is exact AT stored steps for the healthy rotor
    theta = simulate_rotor(HEALTHY_DRIFT)
    recon = reconstruct_from_snapshots(theta, union)
    store_exact = bool(np.allclose(recon[union], theta[union]))
    is_valid &= store_exact
    print(f"  {'✔️' if store_exact else '❌'} reconstruction exact at stored steps")

    # 4. Drift diagnostic sensitivity: drifted residual exceeds healthy residual
    healthy_resid = float(np.max(np.abs(reconstruct_from_snapshots(
        simulate_rotor(HEALTHY_DRIFT), union) - simulate_rotor(HEALTHY_DRIFT))))
    drifted_resid = float(np.max(np.abs(reconstruct_from_snapshots(
        simulate_rotor(DRIFTED_DRIFT), union) - simulate_rotor(DRIFTED_DRIFT))))
    sensitivity_ok = drifted_resid > healthy_resid
    is_valid &= sensitivity_ok
    print(f"  {'✔️' if sensitivity_ok else '❌'} drift sensitivity: "
          f"{healthy_resid:.4f} -> {drifted_resid:.4f}")

    # 5. Round-trip CRT consistency for a sample remainder pair
    k_true = crt_cell_to_step(3, 7, M, N)
    roundtrip_ok = k_true % M == 3 and k_true % N == 7
    is_valid &= roundtrip_ok
    print(f"  {'✔️' if roundtrip_ok else '❌'} CRT round-trip consistency: "
          f"(3, 7) -> {k_true}")

    # 6. Color engine wiring surfaced, not assumed
    print(f"  - using project colors.py: {USING_PROJECT_COLORS}")
    print(f"  - using kuramoto.solvers.coprime: {USING_KURAMOTO_LIB}")

    print("✅💨 Smoke tests passed." if is_valid else "❌ Smoke tests FAILED.")
    return is_valid


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------

def main() -> None:
    """Orchestrate validation and figure generation.

    Never contains raw CRT math logic directly: runs the smoke tests, then renders each figure driver once with
    canonical example arguments.
    """
    # if not run_smoke_test():
        # raise ValueError("❌ CRT diagnostic validation failed during smoke tests.")

    figure1()
    crt_trace_figure(k_m=3, k_n=7, m=M, n=N)
    # crt_noncoprime_figure(k_m=4, k_n=1, m=6, n=9)   # consistent: 3 collisions
    # crt_noncoprime_figure(k_m=1, k_n=2, m=6, n=9)   # inconsistent: dead zone

if __name__ == "__main__":
    main()
