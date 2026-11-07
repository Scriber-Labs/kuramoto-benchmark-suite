"""
ODE solver interface for Kuramoto simulations.

This module exports:
    - ``solve_kuramoto``: a thin interface around SciPy's adaptive RK45 integrator.
    - ``RotorSolver``: an experimental geometric-algebra representation of Kuramoto dynamics using fixed-step Euler
      integration.
"""

from .coprime import (
    CoprimeSampleResult,
    CoprimeSamplerWrapper,
    coprime_reconstruct_frequency,
    detect_spectral_drift,
    extended_gcd,
)
from .quantum_rotor import QuantumRotorSolver, step_quantum_scf
from .rk45 import solve_kuramoto
from .rotor import (
    AdaptiveStatus,
    AdaptiveStepResult,
    RotorSolver,
    fibonacci_word_symbol,
    step_dopri54,
    step_quasi_periodic,
    step_rkmk4,
)

__all__: list[str] = [
    "solve_kuramoto",
    "RotorSolver",
    "step_rkmk4",
    "step_dopri54",
    "step_quasi_periodic",
    "fibonacci_word_symbol",
    "QuantumRotorSolver",
    "step_quantum_scf",
    "CoprimeSampleResult",
    "CoprimeSamplerWrapper",
    "coprime_reconstruct_frequency",
    "detect_spectral_drift",
    "extended_gcd",
]
