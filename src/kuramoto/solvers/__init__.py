"""
ODE solver interface for Kuramoto simulations.

This module exports:
    - ``solve_kuramoto``: a thin interface around SciPy's adaptive RK45 integrator.
    - ``RotorSolver``: an experimental geometric-algebra representation of Kuramoto dynamics using fixed-step Euler
      integration.
"""

from .rk45 import solve_kuramoto
from .rotor import RotorSolver

__all__: list[str] = ["solve_kuramoto", "RotorSolver"]