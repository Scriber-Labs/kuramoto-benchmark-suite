# src/kuramoto/model.py
"""
KuramotoModel - adaptive RK45 simulator for N coupled oscillators.

Supports both classic RK45 integration and experimental Geometric Algebra
rotor representation via the solvers submodule.

See `model.py` discussion on https://scriber-labs.github.io/research-notebook/kuramoto-benchmark/kuramoto_source_code/ .

Author: Eigenscribe
Development note: Initial LLM scaffolding; implementation has been reviewed and adapted for this project.
Review status: Reviewed and maintained by Eigenscribe.
Date: May 2026
"""

from __future__ import annotations

import warnings
from time import time
from typing import Optional, Final, Dict

import numpy as np
from numpy.typing import NDArray

from kuramoto.validation import *

from kuramoto.graphs import graph_stats
from kuramoto.dataset import KuramotoDataset
from kuramoto.solvers import solve_kuramoto, RotorSolver  # ← Updated import
from kuramoto.order_parameter import compute_order_parameter as order_parameter
from kuramoto.utils import get_rng

__all__: list[str] = ["KuramotoModel"]

# ---------------------------------------------------------------------------- #
# Type Aliases
# ---------------------------------------------------------------------------- #
FrequencyArray = NDArray[np.floating]
PhaseArray = NDArray[np.floating]
AdjacencyMatrix = NDArray[np.floating]

# ---------------------------------------------------------------------------- #
# Model Class
# ---------------------------------------------------------------------------- #
class KuramotoModel:
    """
    Simulate the Kuramoto equations with optional additive Gaussian noise.

    Supports both classic RK45 integration and experimental Geometric Algebra
    rotor representation via the `solver_type` parameter.

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
        Note: Not supported by RotorSolver; raises error if solver_type='rotor'.
    random_seed : int, optional
        Seed forwarded to `numpy.random.default_rng`.
    solver_type : str, default 'rk45'
        Integration method: 'rk45' (classic RK45) or 'rotor' (GA-based Euler).
    """

    # -------- class-level defaults ------------------------------------ #
    DEFAULT_FREQ_STD: Final[float] = 1.0
    _STEPS_PER_PERIOD: Final[int] = 20
    _MIN_OUTPUT_POINTS: Final[int] = 500
    _RTOL: Final[float] = 1e-6
    _ATOL: Final[float] = 1e-9

    # ------------------------------------------------------------------ #
    # Constructor
    # ------------------------------------------------------------------ #
    def __init__(
        self,
        n_oscillators: int,
        *,
        natural_frequencies: Optional[FrequencyArray] = None,
        adjacency_matrix: Optional[AdjacencyMatrix] = None,
        coupling_strength: float = 1.0,
        noise_std: float = 0.0,
        random_seed: Optional[int] = None,
        solver_type: str = "rk45",
    ) -> None:
        # ---- validation ------------------------------------------------ #
        if n_oscillators <= 0:
            raise ValueError(f"n_oscillators must be positive, got N={n_oscillators}")
        validate_positive_scalar(coupling_strength, "coupling_strength")
        validate_non_negative_scalar(noise_std, "noise_std")

        if solver_type not in ("rk45", "rotor"):
            raise ValueError(f"solver_type must be 'rk45' or 'rotor', got '{solver_type}'")

        # ---- solver configuration -------------------------------------- #
        self.solver_type = solver_type

        if solver_type == "rotor" and noise_std > 0.0:
            raise ValueError(
                "noise_std > 0 is not supported by RotorSolver. "
                "The GA-based Euler integration does not yet include stochastic "
                "differential equation support. Set noise_std=0 or use solver_type='rk45'."
            )

        # ---- core parameters ------------------------------------------- #
        self.n: Final[int] = n_oscillators
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

        # ---- RotorSolver initialization (if applicable) ---------------- #
        if solver_type == "rotor":
            self.rotor_solver = RotorSolver(
                n_oscillators=n_oscillators,
                dim=2,
                seed=random_seed,
            )

        # ---- placeholders for results ---------------------------------- #
        self.time: NDArray | None = None
        self.phases: NDArray | None = None
        self.derivatives: NDArray | None = None
        self.order_param: NDArray | None = None

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _rhs(self, _t: float, theta: PhaseArray) -> PhaseArray:
        """Vectorized RHS of the Kuramoto model (and optional noise)."""
        delta_theta = theta[None, :] - theta[:, None]
        coupling = np.sum(self.A * np.sin(delta_theta), axis=1)
        dtheta = self.omega + (self.K / self.n) * coupling
        if self.noise_std > 0.0:
            dtheta += self.rng.normal(0.0, self.noise_std, size=self.n)
        return dtheta

    def _max_step(self) -> float:
        """Heuristic step bound based on fastest eigen-frequency."""
        omega_max = float(np.max(np.abs(self.omega)))
        deg_max = int(np.max(np.sum(self.A > 0, axis=1)))
        lambda_max = omega_max * self.K * deg_max
        return np.inf if lambda_max == 0 else (2*np.pi / lambda_max) / self._STEPS_PER_PERIOD

    # ------------------------------------------------------------------ #
    # Public API
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

        points = n_points if n_points is not None else self._MIN_OUTPUT_POINTS
        t_eval = np.linspace(0.0, t_span, points)

        if self.solver_type == "rk45":
            return self._simulate_rk45(t_span, t_eval, points)
        elif self.solver_type == "rotor":
            return self._simulate_rotor(t_span, t_eval, points)
        else:
            raise RuntimeError(f"Unknown solver_type: {self.solver_type}")

    def _simulate_rk45(self, t_span: float, t_eval: NDArray, n_points: int) -> KuramotoDataset:
        """Classic RK45 integration path."""
        max_step = self._max_step()

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
            raise RuntimeError(f"Integration failed: {sol.message}")

        phases = sol.y.T
        derivatives = np.array([self._rhs(t, y) for t, y in zip(t_eval, phases)])
        order_param = order_parameter(phases)

        self.time = t_eval
        self.phases = phases
        self.derivatives = derivatives
        self.order_param = order_param

        net_stats: Dict[str, float] = graph_stats(self.A)

        return KuramotoDataset(
            omega=self.omega,
            theta=phases,
            dtheta=derivatives,
            time=t_eval,
            initial_conditions=self.initial_phases,
            coupling=self.K,
            adjacency=self.A,
            network_stats=net_stats,
            noise_std=self.noise_std,
            freq_pdf=self.freq_pdf,
            phase_pdf="U(0, 2*pi)",
        )

    def _simulate_rotor(self, t_span: float, t_eval: NDArray, n_points: int) -> KuramotoDataset:
        """Geometric Algebra rotor integration path."""
        # Override rotor solver frequencies and initial phases
        self.rotor_solver.omegas = self.omega.copy()
        self.rotor_solver.rotors = [
            np.exp(-self.rotor_solver.B_plane * p / 2.0)
            for p in self.initial_phases
        ]

        # Calculate internal timestep for Euler integration
        dt_internal = float(np.min(np.diff(t_eval))) * 0.1

        sim_times, sim_phases = self.rotor_solver.simulate(
            K=self.K,
            t_eval=t_eval,
            dt_internal=dt_internal,
            enforce_nyquist=True,
        )

        # Compute derivatives numerically via finite differences
        derivatives = np.gradient(sim_phases, axis=0)

        # Compute order parameter across all timesteps
        order_param_computed = order_parameter(sim_phases)

        self.time = sim_times
        self.phases = sim_phases
        self.derivatives = derivatives
        self.order_param = order_param_computed

        net_stats: Dict[str, float] = graph_stats(self.A)

        return KuramotoDataset(
            omega=self.omega,
            theta=sim_phases,
            dtheta=derivatives,
            time=sim_times,
            initial_conditions=self.initial_phases,
            coupling=self.K,
            adjacency=self.A,
            network_stats=net_stats,
            noise_std=0.0,
            freq_pdf=self.freq_pdf,
            phase_pdf="U(0, 2*pi)",
        )

    # ------------------------------------------------------------------ #
    # Niceties
    # ------------------------------------------------------------------ #
    def __repr__(self) -> str:
        sim = "no-run-yet" if self.time is None else f"T={self.time.size}"
        solver_str = f"[{self.solver_type.upper()}]"
        return f"KuramotoModel(N={self.n}, K={self.K:g}, sigma={self.noise_std:g}, {solver_str}, {sim})"

# --------------------------------------------------------------------------- #
# Smoke test
# --------------------------------------------------------------------------- #
def _run_smoke_test() -> None:
    """Sanity check: basic simulation and shape assertions."""
    print("💨 KuramotoModel smoke test")

    # ------------------------------------------------------------------ #
    # 1. RK45: Two-oscillator coupling test
    # ------------------------------------------------------------------ #
    model_rk45 = KuramotoModel(
        n_oscillators=2,
        natural_frequencies=np.zeros(2),
        coupling_strength=1.0,
        random_seed=27,
        solver_type="rk45",
    )

    theta = np.array([0.0, np.pi / 2])
    dtheta = model_rk45._rhs(0.0, theta)

    expected = np.array([0.5, -0.5])

    assert np.allclose(dtheta, expected)
    print(" ... ✔️ RK45 two-oscillator coupling test passed")

    # ------------------------------------------------------------------ #
    # 2. RK45: Basic simulation
    # ------------------------------------------------------------------ #
    mdl_rk45 = KuramotoModel(
        n_oscillators=10,
        coupling_strength=1.8,
        random_seed=27,
        solver_type="rk45",
    )
    ds_rk45 = mdl_rk45.simulate(t_span=4.0)

    assert ds_rk45.theta.shape == (KuramotoModel._MIN_OUTPUT_POINTS, 10)
    assert ds_rk45.dtheta.shape == ds_rk45.theta.shape
    print(" ... ✔️ RK45 shapes OK")

    # ------------------------------------------------------------------ #
    # 3. Rotor: Noise rejection test
    # ------------------------------------------------------------------ #
    try:
        KuramotoModel(
            n_oscillators=10,
            coupling_strength=1.0,
            noise_std=0.1,
            solver_type="rotor",
        )
        print(" ... ✖️ Rotor should reject noise_std > 0")
    except ValueError:
        print(" ... ✔️ Rotor correctly rejects noise_std > 0")

    # ------------------------------------------------------------------ #
    # 4. Rotor: Basic simulation (if clifford installed)
    # ------------------------------------------------------------------ #
    try:
        mdl_rotor = KuramotoModel(
            n_oscillators=10,
            coupling_strength=1.8,
            random_seed=27,
            solver_type="rotor",
        )
        ds_rotor = mdl_rotor.simulate(t_span=4.0)

        assert ds_rotor.theta.shape == (KuramotoModel._MIN_OUTPUT_POINTS, 10)
        assert ds_rotor.dtheta.shape == ds_rotor.theta.shape
        print(" ... ✔️ Rotor shapes OK")
    except ImportError:
        print(" ... ⚠️ Skipped Rotor tests (clifford not installed)")

    # ------------------------------------------------------------------ #
    # 5. Order parameter bounds
    # ------------------------------------------------------------------ #
    assert np.all((mdl_rk45.order_param >= 0) & (mdl_rk45.order_param <= 1))
    print(" ... ✔️ order parameter bounds OK")

    print("\n✅ KuramotoModel smoke test passed")

# ------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------

def main() -> None:
    _run_smoke_test()

if __name__ == "__main__":
    main()