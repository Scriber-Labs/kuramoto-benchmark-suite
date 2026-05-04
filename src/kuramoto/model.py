# src/kuramoto/model.py
"""
KuramotoModel - adaptive RK45 simulator for N coupled oscillators.

See `model.py` discussion on https://scriber-labs.github.io/research-notebook/kuramoto-benchmark/kuramoto_source_code/ .

Author: Eigenscribe
Development note: Initial LLM scaffolding; implementation has been reviewed and adapted for this project.
Review status: Reviewed and maintained by Eigenscribe.
Date: May 2026
"""

from __future__ import annotations

from time import time
# --------------------------------------------------------------------------- #
# Imports & type aliases
# --------------------------------------------------------------------------- #

from typing import Optional, Final, Dict
import numpy as np
from numpy.typing import NDArray

from .validation import *

from .graphs import graph_stats
from .dataset import KuramotoDataset
from .solvers import solve_kuramoto
from .order_parameter import compute_order_parameter as order_parameter
from .utils import get_rng

__all__: list[str] = [
    "KuramotoModel",
]

# ---------------------------------------------------------------------------- #
# 0️⃣ Type Aliases
# ---------------------------------------------------------------------------- #
FrequencyArray = NDArray[np.floating]
PhaseArray      = NDArray[np.floating]
AdjacencyMatrix = NDArray[np.floating]

# --------------------------------------------------------------------------- #
# 1️⃣ Model class
# --------------------------------------------------------------------------- #
class KuramotoModel:
    """
    Simulate the Kuramoto equations with optional additive Gaussian noise.

    Parameters
    ----------
    n_oscillators : int
        Number of phase oscillators (N).
    natural_frequencies : FrequencyArray, optional
        omega array; if None, sampled from N(0, `DEFAULT_FREQ_STD`).
    adjacency_matrix : AdjacencyMatrix, optional
        Network topology; if None, uses a complete graph (diag=0).
    coupling_strength : float, default 1.0
        Global coupling K (> 0).
    noise_std : float, default 0.0
        sigma of additive i.i.d. Gaussian noise on the RHS (>= 0).
    random_seed : int, optional
        Seed forwarded to `numpy.random.default_rng`.
    """

    # -------- class-level defaults ------------------------------------ #
    DEFAULT_FREQ_STD:            Final[float] = 1.0
    _STEPS_PER_PERIOD:           Final[int]   = 20
    _MIN_OUTPUT_POINTS:          Final[int]   = 500
    _RTOL:                       Final[float] = 1e-6
    _ATOL:                       Final[float] = 1e-9

    # ------------------------------------------------------------------ #
    # 🏗️ Constructor
    # ------------------------------------------------------------------ #
    def __init__(
        self,
        n_oscillators: int,
        *,
        natural_frequencies: Optional[FrequencyArray] = None,
        adjacency_matrix:   Optional[AdjacencyMatrix] = None,
        coupling_strength:  float = 1.0,
        noise_std:          float = 0.0,
        random_seed:        Optional[int] = None,
    ) -> None:

        # ---- validation ------------------------------------------------ #
        if n_oscillators <=0:
            raise ValueError(f"❌ n_oscillators must be positive, got N={n_oscillators}")
        validate_positive_scalar(coupling_strength, "coupling_strength")
        validate_non_negative_scalar(noise_std, "noise_std")

        # ---- core parameters ------------------------------------------- #
        self.n: Final[int]   = n_oscillators
        self.K: Final[float] = coupling_strength
        self.noise_std: Final[float] = noise_std
        self.rng = get_rng(random_seed)

        # ---- natural frequencies --------------------------------------- #
        if natural_frequencies is None:
            omega = self.rng.normal(0.0, self.DEFAULT_FREQ_STD, self.n)
            self.freq_pdf = f"N(0,{self.DEFAULT_FREQ_STD})"
        else:
            validate_intrinsic_frequency_array(natural_frequencies, self.n)
            omega = np.asarray(natural_frequencies, dtype=np.float64)
            self.freq_pdf = "user-supplied"
        self.omega: FrequencyArray = omega

        # ---- adjacency matrix ------------------------------------------ #
        if adjacency_matrix is None:
            A = np.ones((self.n, self.n))
            np.fill_diagonal(A, 0.0)
        else:
            validate_adjacency(adjacency_matrix, self.n)
            A = np.asarray(adjacency_matrix, dtype=np.float64)
        self.A: AdjacencyMatrix = A

        # ---- initial conditions ---------------------------------------- #
        self.initial_phases: PhaseArray = self.rng.uniform(0.0, 2*np.pi, self.n)

        # ---- placeholders for results ---------------------------------- #
        self.time:         NDArray | None = None
        self.phases:       NDArray | None = None
        self.derivatives:  NDArray | None = None
        self.order_param:  NDArray | None = None

    # ------------------------------------------------------------------ #
    # 🧩 Internal helpers
    # ------------------------------------------------------------------ #
    def _rhs(self, _t: float, theta: PhaseArray) -> PhaseArray:
        """Vectorized RHS of the Kuramoto model (and optional noise)."""
        delta_theta  = theta[None, :] - theta[:, None]          # pairwise phase differences
        coupling     = np.sum(self.A * np.sin(delta_theta), axis=1)
        dtheta       = self.omega + (self.K / self.n) * coupling
        if self.noise_std > 0.0:
            dtheta += self.rng.normal(0.0, self.noise_std, size=self.n)
        return dtheta

    def _max_step(self) -> float:
        """Heuristic step bound based on fastest eigen-frequency."""
        omega_max = float(np.max(np.abs(self.omega)))
        deg_max   = int(np.max(np.sum(self.A > 0, axis=1)))
        lambda_max = omega_max * self.K * deg_max
        return np.inf if lambda_max == 0 else (2*np.pi / lambda_max) / self._STEPS_PER_PERIOD

    # ------------------------------------------------------------------ #
    # 🌐 Public API
    # ------------------------------------------------------------------ #
    def simulate(self, t_span: float, n_points: Optional[int] = None) -> KuramotoDataset:
        """
        Integrate up to `t_span` seconds and return a `KuramotoDataset`.

        Parameters
        ----------
        t_span : float
            Total simulation time (must be > 0).
        n_points : int, optional
            Number of time points to output. If None, uses `_MIN_OUTPUT_POINTS`.

        Returns
        -------
        KuramotoDataset
            Fully populated immutable dataset object.
        """
        validate_positive_scalar(t_span, "t_span")

        # ---- prepare solver args -------------------------------------- #
        max_step = self._max_step()
        points = n_points if n_points is not None else self._MIN_OUTPUT_POINTS
        t_eval   = np.linspace(0.0, t_span, points)

        sol = solve_kuramoto(
            rhs=self._rhs,
            y0=self.initial_phases,
            t_span=t_span,
            t_eval=t_eval,
            rtol=self._RTOL,
            atol=self._ATOL,
            max_step=max_step,
        )
        if not sol.success:
            raise RuntimeError(f"❌ Integration failed: {sol.message}")

        # ---- extract results ------------------------------------------ #
        self.time   = sol.t
        self.phases = sol.y.T
        self.derivatives = np.array([self._rhs(t, y) for t, y in zip(self.time, self.phases)])
        self.order_param = order_parameter(self.phases)

        # ---- compute network stats ------------------------------------ #
        net_stats: Dict[str, float] = graph_stats(self.A)

        # ---- package & return ----------------------------------------- #
        return KuramotoDataset(
            omega             = self.omega,
            theta             = self.phases,
            dtheta            = self.derivatives,
            time              = self.time,
            initial_conditions = self.initial_phases,
            coupling          = self.K,
            adjacency         = self.A,
            network_stats     = net_stats,
            noise_std         = self.noise_std,
            freq_pdf          = self.freq_pdf,
            phase_pdf         = "U(0, 2*pi)",
        )

    # ------------------------------------------------------------------ #
    # 🌺 Niceties
    # ------------------------------------------------------------------ #
    def __repr__(self) -> str:
        sim = "no-run-yet" if self.time is None else f"T={self.time.size}"
        return f"KuramotoModel(N={self.n}, K={self.K:g}, sigma={self.noise_std:g}, {sim})"

# --------------------------------------------------------------------------- #
# 2️⃣ Smoke test
# --------------------------------------------------------------------------- #
def _run_smoke_test() -> None:
    """Sanity check: basic simulation and shape assertations."""
    print("💨 Kuramoto smoke test")
    mdl = KuramotoModel(n_oscillators=8, coupling_strength=1.8, random_seed=27)
    ds  = mdl.simulate(t_span=4.0)

    assert ds.theta.shape == (KuramotoModel._MIN_OUTPUT_POINTS, 8)
    assert ds.dtheta.shape == ds.theta.shape
    print("    ✔️ shapes OK")

    # quick numeric check: r(t) in [0,1]
    assert np.all((mdl.order_param >= 0) & (mdl.order_param <= 1))
    print("    ✔️ order parameter bounds OK")

    print("✅ KuramotoModel smoke test passed")

if __name__ == "__main__":
    _run_smoke_test()
