# kuramoto/model.py
from __future__ import annotations

from typing import Final, Optional, Dict, Any
import numpy as np
from scipy.integrate import solve_ivp

from .types import (
    AdjacencyMatrix,
    FrequencyArray,
    PhaseArray,
    TimeArray,
    DerivativeArray,
    KuramotoDataset,
)
from .validation import (
    validate_positive_scalar,
    validate_non_negative_scalar,
    validate_intrinsic_frequency_array,
    validate_adjacency,
)

class KuramotoModel:
    """
    Kuramoto model with adaptive RK45 integration and automatic step sizing.
    
    Implements the dynamics:
        dθᵢ/dt = ωᵢ + (K/N) Σⱼ Aᵢⱼ sin(θⱼ - θᵢ) + ξᵢ(t)
    
    where ξᵢ(t) is optional Gaussian noise.
    
    Features:
        - Adaptive step sizing (RK45) with heuristic max_step based on λ_max.
        - Support for additive phase noise.
        - Returns both phases and derivatives.
        - Strict input validation.
    """
    
    DEFAULT_FREQ_STD: Final[float] = 1.0
    DEFAULT_STEPS_PER_PERIOD: Final[int] = 20
    DEFAULT_MIN_POINTS: Final[int] = 500
    DEFAULT_MAX_POINTS: Final[int] = 2000

    def __init__(
        self,
        n_oscillators: int,
        natural_frequencies: Optional[FrequencyArray] = None,
        adjacency_matrix: Optional[AdjacencyMatrix] = None,
        coupling_strength: float = 1.0,
        noise_std: float = 0.0,
        random_seed: Optional[int] = None,
    ) -> None:
        """Initialize Kuramoto model with validation."""
        if n_oscillators <= 0:
            raise ValueError(f"n_oscillators must be positive, got {n_oscillators}")
        
        validate_positive_scalar(coupling_strength, "coupling_strength")
        validate_non_negative_scalar(noise_std, "noise_std")

        self.n: Final[int] = n_oscillators
        self.K: Final[float] = coupling_strength
        self.noise_std: Final[float] = noise_std
        
        # Frequencies
        if natural_frequencies is None:
            self.omega: FrequencyArray = np.random.default_rng(random_seed).normal(
                0.0, self.DEFAULT_FREQ_STD, self.n
            )
        else:
            omega_arr = np.asarray(natural_frequencies, dtype=np.float64)
            validate_intrinsic_frequency_array(omega_arr, self.n)
            self.omega = omega_arr

        # Adjacency
        if adjacency_matrix is None:
            A = np.ones((self.n, self.n))
            np.fill_diagonal(A, 0)
            self.A: AdjacencyMatrix = A
        else:
            A_arr = np.asarray(adjacency_matrix, dtype=np.float64)
            validate_adjacency(A_arr, self.n)
            self.A = A_arr

        # RNG
        self.rng = np.random.default_rng(random_seed)
        
        # Initial phases
        self.initial_phases: PhaseArray = self.rng.uniform(0.0, 2 * np.pi, self.n)

        # Results placeholders
        self.times: Optional[TimeArray] = None
        self.phases: Optional[PhaseArray] = None
        self.derivatives: Optional[DerivativeArray] = None
        self.order_param: Optional[TimeArray] = None

    def _rhs(
        self,
        t: float,
        phases: PhaseArray,
    ) -> PhaseArray:
        """
        Compute the right-hand side of the Kuramoto equations.
        """
        # Vectorized coupling: Σⱼ Aᵢⱼ sin(θⱼ - θᵢ)
        phase_diff = phases[None, :] - phases[:, None]
        coupling_term = self.A * np.sin(phase_diff)
        coupling_sum = np.sum(coupling_term, axis=1)
        
        dtheta = self.omega + (self.K / self.n) * coupling_sum
        
        # Add noise if requested
        if self.noise_std > 0.0:
            dtheta += self.rng.normal(0.0, self.noise_std, size=self.n)
            
        return dtheta

    def _estimate_max_step(
        self,
        steps_per_period: int = DEFAULT_STEPS_PER_PERIOD,
    ) -> float:
        """
        Estimate a safe maximum time step based on the fastest timescale.
        """
        freq_max = np.max(np.abs(self.omega))
        max_deg = np.max(np.sum(self.A > 0, axis=1))
        lambda_max = freq_max + self.K * max_deg

        if lambda_max <= 0:
            return np.inf
        
        T_eff = 2 * np.pi / lambda_max
        return T_eff / steps_per_period

    def simulate(
        self,
        t_span: float,
        rtol: float = 1e-6,
        atol: float = 1e-9,
        max_step: Optional[float] = None,
        steps_per_period: int = DEFAULT_STEPS_PER_PERIOD,
        min_time_points: int = DEFAULT_MIN_POINTS,
        max_time_points: int = DEFAULT_MAX_POINTS,
    ) -> KuramotoDataset:
        """
        Run the simulation using adaptive RK45.
        """
        validate_positive_scalar(t_span, "t_span")
        
        if max_step is None:
            max_step = self._estimate_max_step(steps_per_period)
        
        points_per_unit = min_time_points / 10.0
        n_points = min(max_time_points, max(min_time_points, int(points_per_unit * t_span)))
        t_eval = np.linspace(0.0, t_span, n_points)
        
        sol = solve_ivp(
            fun=lambda t, y: self._rhs(t, y),
            t_span=(0.0, t_span),
            y0=self.initial_phases,
            method='RK45',
            rtol=rtol,
            atol=atol,
            max_step=max_step,
            t_eval=t_eval,
        )
        
        if not sol.success:
            raise RuntimeError(f"Integration failed: {sol.message}")

        self.times = sol.t
        self.phases = sol.y.T
        
        self.derivatives = np.array([self._rhs(t, self.phases[i]) for i, t in enumerate(self.times)])
        self.order_param = np.abs(np.mean(np.exp(1j * self.phases), axis=1))
        
        n_edges = np.sum(self.A > 0) // 2
        avg_deg = np.mean(np.sum(self.A > 0, axis=1))
        network_stats = {
            "n_nodes": self.n,
            "n_edges": int(n_edges),
            "avg_degree": float(avg_deg),
            "density": float(n_edges / (self.n * (self.n - 1) / 2)) if self.n > 1 else 0.0
        }

        return KuramotoDataset(
            omega=self.omega,
            theta=self.phases,
            dtheta=self.derivatives,
            time=self.times,
            initial_conditions=self.initial_phases,
            coupling=self.K,
            adjacency=self.A,
            network_stats=network_stats,
            noise_std=self.noise_std,
            freq_pdf="user-specified",
            phase_pdf="uniform [0, 2*pi)",
        )

    def order_parameter(
        self,
        phases: Optional[PhaseArray] = None,
    ) -> float | TimeArray:
        """Compute the Kuramoto order parameter r(t)."""
        if phases is None:
            if self.phases is None:
                raise RuntimeError("No simulation results available. Run simulate() first.")
            phases = self.phases
        
        phases_arr = np.asarray(phases, dtype=np.complex128)
        if phases_arr.ndim == 1:
            return float(np.abs(np.mean(np.exp(1j * phases_arr))))
        elif phases_arr.ndim == 2:
            return np.abs(np.mean(np.exp(1j * phases_arr), axis=1))
        else:
            raise ValueError(f"Phases must be 1D or 2D, got {phases_arr.shape}")
