# New Target Structure:
```aiignore
kuramoto/
  api.py                # stays (wrapper function)
  model.py              # NEW → KuramotoModel class
  dataset.py            # NEW → KuramotoDataset dataclass
  solvers.py            # NEW → solve_ivp wrapper
  order_parameter.py    # NEW → r(t)
  graphs.py             # reuse
  validation.py         # reuse (maybe extend)
  utils.py              # reuse
```

# Script for Streamlit App
```python
"""
Kuramoto model for coupled phase oscillators on arbitrary network topologies.

The model computes three families of quantities:
    1. **Phase trajectories**           `θ_i(t)`
    2. **Order parameter**              `r(t)` (synchronization measure)
    3. **Coupling dynamics**            `dθ_i/dt`

All three quantities emerge from the network topology (adjacency matrix) and
natural frequency distribution. The code purposefully employs a clean,
"over-engineered" house style so that each component can be independently
tested and swapped out later (e.g., different coupling functions, different
integrators, different network structures, etc.).

Author: Eigenscribe
Development note: LLM assistance was used during construction; implementation
has been reviewed and adapted for this project.
Review status: Reviewed and maintained by Eigenscribe.
Date: 04-2026
"""

from __future__ import annotations

from typing import Final, Optional, Protocol, Dict, Any
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

__all__: list[str] = [
    "KuramotoModel",
    "KuramotoDataset",
    "generate_kuramoto_dataset",
    "compute_order_parameter",
]

# ------------------------------------------------------------------------------
# 0️⃣ Type Aliases and Protocols
# ------------------------------------------------------------------------------
AdjacencyMatrix = NDArray[np.floating]
FrequencyArray = NDArray[np.floating]
PhaseArray = NDArray[np.floating]
TimeArray = NDArray[np.floating]
DerivativeArray = NDArray[np.floating]

@dataclass
class KuramotoDataset:
    """
    Container for Kuramoto simulation results.
    
    Matches the output format of the legacy benchmark generator for compatibility.
    """
    omega: FrequencyArray
    theta: PhaseArray
    dtheta: DerivativeArray
    time: TimeArray
    initial_conditions: PhaseArray
    coupling: float
    adjacency: AdjacencyMatrix
    network_stats: Dict[str, Any]
    noise_std: float
    freq_pdf: str
    phase_pdf: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization or legacy compatibility."""
        return {
            "omega": self.omega,
            "theta": self.theta,
            "dtheta": self.dtheta,
            "time": self.time,
            "initial_conditions": self.initial_conditions,
            "coupling": self.coupling,
            "adjacency": self.adjacency,
            "network_stats": self.network_stats,
            "noise_std": self.noise_std,
            "freq_pdf": self.freq_pdf,
            "phase_pdf": self.phase_pdf,
        }

# ------------------------------------------------------------------------------
# 1️⃣ Validation Helpers (Ported from benchmark)
# ------------------------------------------------------------------------------

def _validate_positive_scalar(value: float, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")

def _validate_non_negative_scalar(value: float, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")

def _validate_adjacency(A: AdjacencyMatrix, n: int) -> None:
    if A.shape != (n, n):
        raise ValueError(f"Adjacency matrix shape {A.shape} does not match n={n}")
    if not np.allclose(A, A.T):
        raise ValueError("Adjacency matrix must be symmetric for undirected graphs")

def _validate_frequencies(omega: FrequencyArray, n: int) -> None:
    if omega.shape != (n,):
        raise ValueError(f"Frequencies shape {omega.shape} does not match n={n}")

# ------------------------------------------------------------------------------
# 2️⃣ Core Model Class
# ------------------------------------------------------------------------------

class KuramotoModel:
    """
    Kuramoto model with adaptive RK45 integration and automatic step sizing.
    
    Implements the dynamics:
        dθᵢ/dt = ωᵢ + (K/N) Σⱼ Aᵢⱼ sin(θⱼ - θᵢ) + ξᵢ(t)
    
    where ξᵢ(t) is optional Gaussian noise.
    
    Features:
        - Adaptive step sizing (RK45) with heuristic max_step based on λ_max.
        - Support for additive phase noise.
        - Returns both phases and derivatives (compatible with benchmark).
        - Strict input validation.
    
    Parameters
    ----------
    n_oscillators : int
        Number of oscillators.
    natural_frequencies : FrequencyArray, optional
        Natural frequencies. If None, sampled from N(0, 1).
    adjacency_matrix : AdjacencyMatrix, optional
        Network topology. If None, uses complete graph (all-to-all).
    coupling_strength : float, default=1.0
        Global coupling constant K.
    noise_std : float, default=0.0
        Standard deviation of additive Gaussian noise.
    random_seed : int, optional
        Seed for reproducibility.
    
    Attributes
    ----------
    n : int
        Number of oscillators.
    A : AdjacencyMatrix
        Adjacency matrix.
    omega : FrequencyArray
        Natural frequencies.
    K : float
        Coupling strength.
    noise_std : float
        Noise level.
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
        
        _validate_positive_scalar(coupling_strength, "coupling_strength")
        _validate_non_negative_scalar(noise_std, "noise_std")

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
            _validate_frequencies(omega_arr, self.n)
            self.omega = omega_arr

        # Adjacency
        if adjacency_matrix is None:
            A = np.ones((self.n, self.n))
            np.fill_diagonal(A, 0)
            self.A: AdjacencyMatrix = A
        else:
            A_arr = np.asarray(adjacency_matrix, dtype=np.float64)
            _validate_adjacency(A_arr, self.n)
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
        
        Includes optional additive noise if noise_std > 0.
        Note: For strict SDE integration, noise should be handled differently,
        but for dataset generation with small dt, additive noise on RHS is acceptable.
        """
        # Vectorized coupling: Σⱼ Aᵢⱼ sin(θⱼ - θᵢ)
        # phase_diff[i, j] = θⱼ - θᵢ
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
        
        λ_max ≈ max(|ω|) + K * max_degree
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
        
        Parameters
        ----------
        t_span : float
            Total simulation time.
        rtol : float
            Relative tolerance.
        atol : float
            Absolute tolerance.
        max_step : float, optional
            Maximum step size. If None, auto-calculated.
        steps_per_period : int
            Steps per fastest period for auto-calculation.
        min_time_points : int
            Minimum output points.
        max_time_points : int
            Maximum output points (performance cap).
        
        Returns
        -------
        KuramotoDataset
            Container with phases, derivatives, time, and metadata.
        """
        _validate_positive_scalar(t_span, "t_span")
        
        # Auto-calculate max_step if not provided
        if max_step is None:
            max_step = self._estimate_max_step(steps_per_period)
        
        # Scale output points
        points_per_unit = min_time_points / 10.0
        n_points = min(max_time_points, max(min_time_points, int(points_per_unit * t_span)))
        t_eval = np.linspace(0.0, t_span, n_points)
        
        # Reset RNG for this run if noise is enabled
        if self.noise_std > 0.0:
            # Note: For true reproducibility with noise, we'd need to seed the solver's noise
            # Here we just use the instance RNG which was seeded in __init__
            pass

        # Solve
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

        # Extract results
        self.times = sol.t
        self.phases = sol.y.T  # Shape: (T, N)
        
        # Compute derivatives at output points (re-evaluate RHS)
        # Note: solve_ivp doesn't return derivatives at t_eval directly, so we re-eval
        self.derivatives = np.array([self._rhs(t, self.phases[i]) for i, t in enumerate(self.times)])
        
        # Compute order parameter
        self.order_param = np.abs(np.mean(np.exp(1j * self.phases), axis=1))
        
        # Compute graph stats
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
        """
        Compute the Kuramoto order parameter r(t).
        
        Parameters
        ----------
        phases : PhaseArray, optional
            Phases to analyze. If None, uses stored simulation results.
        
        Returns
        -------
        float or TimeArray
            Order parameter value(s).
        """
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

# ------------------------------------------------------------------------------
# 3️⃣ Convenience Function (Benchmark Compatibility)
# ------------------------------------------------------------------------------

def generate_kuramoto_dataset(
    n_oscillators: int,
    natural_frequencies: FrequencyArray,
    coupling: float,
    timesteps: int,
    dt: float,
    adjacency: Optional[AdjacencyMatrix] = None,
    noise_std: float = 0.0,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate a synthetic phase time series dataset (Benchmark Compatible).
    
    This function wraps the `KuramotoModel` to provide the exact dictionary
    output format expected by legacy benchmark scripts.
    
    Parameters
    ----------
    n_oscillators : int
        Number of oscillators.
    natural_frequencies : FrequencyArray
        Intrinsic frequencies.
    coupling : float
        Coupling strength K.
    timesteps : int
        Number of time steps (used to estimate t_span).
    dt : float
        Integration step (used to estimate t_span).
    adjacency : AdjacencyMatrix, optional
        Network topology.
    noise_std : float
        Noise level.
    seed : int, optional
        Random seed.
    
    Returns
    -------
    dict[str, Any]
        Dictionary with keys: 'omega', 'theta', 'dtheta', 'time', etc.
    """
    # Estimate t_span from timesteps and dt
    t_span = timesteps * dt
    
    model = KuramotoModel(
        n_oscillators=n_oscillators,
        natural_frequencies=natural_frequencies,
        adjacency_matrix=adjacency,
        coupling_strength=coupling,
        noise_std=noise_std,
        random_seed=seed,
    )
    
    # Run simulation
    dataset = model.simulate(t_span=t_span)
    
    # Return as dictionary for legacy compatibility
    return dataset.to_dict()

# ------------------------------------------------------------------------------
# 4️⃣ Smoke Test
# ------------------------------------------------------------------------------

def _run_smoke_test() -> None:
    """Sanity check for KuramotoModel."""
    np.random.seed(42)
    
    # Test 1: Basic simulation
    model = KuramotoModel(n_oscillators=10, coupling_strength=2.0, random_seed=123)
    dataset = model.simulate(t_span=5.0)
    
    print("✔️ KuramotoModel smoke test:")
    print(f"   Shape theta: {dataset.theta.shape}")
    print(f"   Shape dtheta: {dataset.dtheta.shape}")
    print(f"   Final r: {dataset.order_param[-1]:.3f}")
    
    # Test 2: Noise
    model_noise = KuramotoModel(n_oscillators=10, noise_std=0.1, random_seed=456)
    dataset_noise = model_noise.simulate(t_span=5.0)
    print(f"   With noise final r: {dataset_noise.order_param[-1]:.3f}")
    
    # Test 3: Legacy compatibility
    legacy_data = generate_kuramoto_dataset(
        n_oscillators=10,
        natural_frequencies=model.omega,
        coupling=2.0,
        timesteps=100,
        dt=0.05,
        seed=789
    )
    assert "theta" in legacy_data
    assert "dtheta" in legacy_data
    print("   ✅ Legacy compatibility check passed.")

def main() -> None:
    """Entry point."""
    _run_smoke_test()

if __name__ == "__main__":
    main()

```