from __future__ import annotations

from typing import Optional, Dict, Any
import numpy as np

from .validation import (
    validate_positive_scalar,
    validate_non_negative_scalar,
    validate_adjacency,
    validate_intrinsic_frequency_array,
)
from .graphs import graph_stats
from .dataset import KuramotoDataset
from .solvers import solve_kuramoto
from .order_parameter import compute_order_parameter

class KuramotoModel:
    DEFAULT_FREQ_STD = 1.0
    DEFAULT_STEPS_PER_PERIOD = 20
    DEFAULT_MIN_POINTS = 500
    DEFAULT_MAX_POINTS = 2000

    def __init__(
        self,
        n_oscillators: int,
        natural_frequencies: Optional[np.ndarray] = None,
        adjacency_matrix: Optional[np.ndarray] = None,
        coupling_strength: float = 1.0,
        noise_std: float = 0.0,
        random_seed: Optional[int] = None,
    ) -> None:
        if n_oscillators <= 0:
            raise ValueError("n_oscillators must be positive")

        validate_positive_scalar(coupling_strength, "coupling_strength")
        validate_non_negative_scalar(noise_std, "noise_std")

        self.n = n_oscillators
        self.K = coupling_strength
        self.noise_std = noise_std

        rng = np.random.default_rng(random_seed)

        if natural_frequencies is None:
            self.omega = rng.normal(0.0, self.DEFAULT_FREQ_STD, self.n)
        else:
            validate_intrinsic_frequency_array(natural_frequencies, self.n)
            self.omega = natural_frequencies

        if adjacency_matrix is None:
            A = np.ones((self.n, self.n))
            np.fill_diagonal(A, 0)
            self.A = A
        else:
            validate_adjacency(adjacency_matrix, self.n)
            self.A = adjacency_matrix

        self.rng = rng
        self.initial_phases = rng.uniform(0.0, 2 * np.pi, self.n)

        self.times = None
        self.phases = None
        self.derivatives = None
        self.order_param = None

    def _rhs(self, t, phases):
        phase_diff = phases[None, :] - phases[:, None]
        coupling_term = self.A * np.sin(phase_diff)
        coupling_sum = np.sum(coupling_term, axis=1)

        dtheta = self.omega + (self.K / self.n) * coupling_sum

        if self.noise_std > 0.0:
            dtheta += self.rng.normal(0.0, self.noise_std, size=self.n)

        return dtheta

    def _estimate_max_step(self):
        freq_max = np.max(np.abs(self.omega))
        max_deg = np.max(np.sum(self.A > 0, axis=1))
        lambda_max = freq_max + self.K * max_deg

        if lambda_max <= 0:
            return np.inf

        T_eff = 2 * np.pi / lambda_max
        return T_eff / self.DEFAULT_STEPS_PER_PERIOD

    def simulate(
        self,
        t_span: float,
        rtol: float = 1e-6,
        atol: float = 1e-9,
        max_step: Optional[float] = None,
    ) -> KuramotoDataset:
        validate_positive_scalar(t_span, "t_span")

        if max_step is None:
            max_step = self._estimate_max_step()

        n_points = self.DEFAULT_MIN_POINTS
        t_eval = np.linspace(0.0, t_span, n_points)

        sol = solve_kuramoto(
            rhs=lambda t, y: self._rhs(t, y),
            y0=self.initial_phases,
            t_span=t_span,
            t_eval=t_eval,
            rtol=rtol,
            atol=atol,
            max_step=max_step,
        )

        if not sol.success:
            raise RuntimeError(sol.message)

        self.times = sol.t
        self.phases = sol.y.T
        self.derivatives = np.array(
            [self._rhs(t, self.phases[i]) for i, t in enumerate(self.times)]
        )
        self.order_param = compute_order_parameter(self.phases)

        return KuramotoDataset(
            omega=self.omega,
            theta=self.phases,
            dtheta=self.derivatives,
            time=self.times,
            initial_conditions=self.initial_phases,
            coupling=self.K,
            adjacency=self.A,
            network_stats=graph_stats(self.A),
            noise_std=self.noise_std,
            freq_pdf="user-specified",
            phase_pdf="uniform [0, 2*pi)",
        )