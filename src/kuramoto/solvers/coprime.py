# src/kuramoto/solvers/coprime.py
"""
Coprime Time-Domain Sampler Wrapper and CRT Frequency Reconstruction.

Implements dual-channel coprime time-domain sub-Nyquist sampling (Sampler A at step
interval N, Sampler B at step interval M with gcd(M, N) = 1) around Kuramoto
integrators, reducing memory footprints from O(MN) down to O(M + N) snapshots.
Reconstructs true frequency indices via the Chinese Remainder Theorem (CRT) and
provides high-sensitivity failure-mode diagnostics for geometric rotor drift.

Author: Eigenscribe & Junie
Date: 10-2026
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Final

import numpy as np
from numpy.typing import NDArray

from kuramoto.validation import (
    validate_non_negative_scalar,
    validate_positive_scalar,
)

if TYPE_CHECKING:
    from kuramoto.solvers.rotor import RotorSolver

__all__: list[str] = [
    "CoprimeSampleResult",
    "CoprimeSamplerWrapper",
    "coprime_reconstruct_frequency",
    "detect_spectral_drift",
    "extended_gcd",
]

# ---------------------------------------------------------------------------- #
# 0️⃣ / 🎭 Definitions, Constants & Types
# ---------------------------------------------------------------------------- #

PhaseArray = NDArray[np.floating]
TimeArray = NDArray[np.floating]
ComplexArray = NDArray[np.complexfloating]

DEFAULT_COPRIME_M: Final[int] = 7
DEFAULT_COPRIME_N: Final[int] = 11


@dataclass(frozen=True)
class CoprimeSampleResult:
    """
    Structured container holding coprime sub-sampled simulation streams.

    Attributes
    ----------
    t_a : TimeArray
        Time stamps for Sampler A (sampled every N integration steps).
    order_parameter_a : ComplexArray | NDArray[np.floating]
        Order parameter trajectory captured by Sampler A.
    t_b : TimeArray
        Time stamps for Sampler B (sampled every M integration steps).
    order_parameter_b : ComplexArray | NDArray[np.floating]
        Order parameter trajectory captured by Sampler B.
    M : int
        Subsampling step stride for Sampler B (gcd(M, N) == 1).
    N : int
        Subsampling step stride for Sampler A (gcd(M, N) == 1).
    dt : float
        Base integration timestep size.
    total_steps : int
        Total dense integration steps computed during simulation.
    phases_a : PhaseArray | None
        Phase trajectory captured by Sampler A (if recorded).
    phases_b : PhaseArray | None
        Phase trajectory captured by Sampler B (if recorded).
    """

    t_a: TimeArray
    order_parameter_a: ComplexArray | NDArray[np.floating]
    t_b: TimeArray
    order_parameter_b: ComplexArray | NDArray[np.floating]
    M: int
    N: int
    dt: float
    total_steps: int
    phases_a: PhaseArray | None = None
    phases_b: PhaseArray | None = None

    @property
    def total_snapshots(self) -> int:
        """Total number of snapshots stored across both samplers."""
        return len(self.t_a) + len(self.t_b)

    @property
    def dense_snapshots(self) -> int:
        """Number of snapshots that a full dense sampling would have required."""
        return self.total_steps + 1

    @property
    def compression_ratio(self) -> float:
        """Ratio of stored coprime snapshots relative to full dense snapshots."""
        if self.dense_snapshots == 0:
            return 0.0
        return float(self.total_snapshots / self.dense_snapshots)

    def reconstruct_frequency(
        self,
        k_m: int | NDArray[np.integer],
        k_n: int | NDArray[np.integer],
    ) -> int | NDArray[np.integer]:
        """
        Reconstruct true frequency index from observed aliases k_m and k_n.

        Parameters
        ----------
        k_m : int | NDArray[np.integer]
            Aliased frequency index observed by Sampler B (stride M).
        k_n : int | NDArray[np.integer]
            Aliased frequency index observed by Sampler A (stride N).

        Returns
        -------
        int | NDArray[np.integer]
            True unaliased frequency index within [0, M * N - 1].
        """
        return coprime_reconstruct_frequency(k_m=k_m, k_n=k_n, M=self.M, N=self.N)


# ---------------------------------------------------------------------------- #
# 1️⃣ Public API
# ---------------------------------------------------------------------------- #


def extended_gcd(x: int, y: int) -> tuple[int, int, int]:
    """
    Compute gcd(x, y) and Bézout coefficients (a, b) such that a*x + b*y = gcd(x, y).

    Parameters
    ----------
    x : int
        First integer.
    y : int
        Second integer.

    Returns
    -------
    tuple[int, int, int]
        ``(gcd, a, b)`` where ``a * x + b * y == gcd``.

    Raises
    ------
    ValueError
        If both x and y are zero.
    """
    if x == 0 and y == 0:
        raise ValueError("Extended GCD is undefined for x = 0 and y = 0.")

    def _ext_gcd(a_val: int, b_val: int) -> tuple[int, int, int]:
        if a_val == 0:
            return b_val, 0, 1
        g, a1, b1 = _ext_gcd(b_val % a_val, a_val)
        return g, b1 - (b_val // a_val) * a1, a1

    # Work with absolute values to guarantee positive gcd
    sign_x = 1 if x >= 0 else -1
    sign_y = 1 if y >= 0 else -1

    g, a, b = _ext_gcd(abs(x), abs(y))
    return g, a * sign_x, b * sign_y


def coprime_reconstruct_frequency(
    k_m: int | NDArray[np.integer],
    k_n: int | NDArray[np.integer],
    M: int,
    N: int,
) -> int | NDArray[np.integer]:
    """
    Reconstruct true frequency index from coprime aliases using CRT and Bézout identity.

    Given coprime sampling strides M and N (with gcd(M, N) = 1) and observed
    sub-Nyquist frequency aliases:
        k_m = k_true % M  (observed by Sampler B)
        k_n = k_true % N  (observed by Sampler A)

    The Bézout identity yields coefficients a, b such that:
        a * M + b * N = 1

    Which implies:
        b * N == 1 (mod M)  and  b * N == 0 (mod N)
        a * M == 1 (mod N)  and  a * M == 0 (mod M)

    The unique unaliased index k_true in [0, M*N - 1] is reconstructed via:
        k_true = (k_m * b * N + k_n * a * M) % (M * N)

    Parameters
    ----------
    k_m : int | NDArray[np.integer]
        Observed alias modulo M (from Sampler B).
    k_n : int | NDArray[np.integer]
        Observed alias modulo N (from Sampler A).
    M : int
        Subsampling step stride for Sampler B (must be positive and coprime to N).
    N : int
        Subsampling step stride for Sampler A (must be positive and coprime to M).

    Returns
    -------
    int | NDArray[np.integer]
        True reconstructed frequency index in [0, M * N - 1].

    Raises
    ------
    ValueError
        If M or N <= 0, or if gcd(M, N) != 1.
    """
    if M <= 0 or N <= 0:
        raise ValueError(
            f"Strides M and N must be positive integers, got M={M}, N={N}."
        )

    g, a, b = extended_gcd(M, N)
    if g != 1:
        raise ValueError(
            f"Strides M={M} and N={N} are not coprime (gcd = {g}). "
            "CRT frequency reconstruction requires gcd(M, N) == 1."
        )

    # CRT reconstruction step
    # k_m * (b * N) recovers remainder modulo M (since b * N == 1 mod M and == 0 mod N)
    # k_n * (a * M) recovers remainder modulo N (since a * M == 1 mod N and == 0 mod M)
    modulus = M * N
    k_true = (k_m * (b * N) + k_n * (a * M)) % modulus
    return k_true


class CoprimeSamplerWrapper:
    """
    Time-domain coprime sampling wrapper around Kuramoto / Geometric Rotor integrators.

    Instead of maintaining dense trajectory histories of size O(MN), this wrapper
    evaluates state snapshots across dual asynchronous coprime channels:
    - Channel A: Samples state or order parameter every N integration steps.
    - Channel B: Samples state or order parameter every M integration steps.

    Parameters
    ----------
    solver : RotorSolver | Any
        Underlying integrator instance (e.g., `RotorSolver` or stepping model).
    M : int, default=7
        Sampling stride for Channel B.
    N : int, default=11
        Sampling stride for Channel A.
    record_phases : bool, default=False
        Whether to store oscillator phase vectors theta(t) alongside order parameters.
    """

    def __init__(
        self,
        solver: RotorSolver | Any,
        M: int = DEFAULT_COPRIME_M,
        N: int = DEFAULT_COPRIME_N,
        record_phases: bool = False,
    ) -> None:
        validate_positive_scalar(M, "M")
        validate_positive_scalar(N, "N")

        g, _, _ = extended_gcd(int(M), int(N))
        if g != 1:
            raise ValueError(
                f"Coprime strides M={M} and N={N} must satisfy gcd(M, N) == 1, got gcd = {g}."
            )

        self.solver = solver
        self.M = int(M)
        self.N = int(N)
        self.record_phases = bool(record_phases)

    def simulate(
        self,
        K: float,
        dt: float,
        total_steps: int | None = None,
        cycles: int = 1,
        method: str = "fast",
        custom_stepper: Callable[[float, float], None] | None = None,
    ) -> CoprimeSampleResult:
        """
        Execute forward simulation with dual coprime subsampling.

        Parameters
        ----------
        K : float
            Coupling strength.
        dt : float
            Internal integration time step.
        total_steps : int, optional
            Total dense steps to simulate. If None, defaults to `cycles * M * N`.
        cycles : int, default=1
            Number of full coprime periods (M * N steps per cycle) if `total_steps` is None.
        method : str, default='fast'
            Integration stepper method for `RotorSolver` (e.g. 'fast', 'rkmk4', 'geometric').
        custom_stepper : Callable[[float, float], None], optional
            Optional custom stepping function with signature `stepper(K, dt)`.

        Returns
        -------
        CoprimeSampleResult
            Container with time arrays, order parameters, and phase streams.
        """
        validate_non_negative_scalar(K, "K")
        validate_positive_scalar(dt, "dt")

        if total_steps is None:
            if cycles <= 0:
                raise ValueError(f"cycles must be positive, got {cycles}.")
            total_steps = cycles * (self.M * self.N)
        else:
            validate_positive_scalar(total_steps, "total_steps")
            total_steps = int(total_steps)

        # Resolve stepper method
        step_fn = self._resolve_stepper(method, custom_stepper)

        # Preallocate stream buffers
        t_a_list: list[float] = []
        op_a_list: list[complex] = []
        phases_a_list: list[PhaseArray] | None = [] if self.record_phases else None

        t_b_list: list[float] = []
        op_b_list: list[complex] = []
        phases_b_list: list[PhaseArray] | None = [] if self.record_phases else None

        # Helper to extract current state
        def _record_sample(
            step_idx: int,
            current_t: float,
            to_a: bool,
            to_b: bool,
        ) -> None:
            op = self._get_order_parameter()
            phases = self._get_phases() if self.record_phases else None

            if to_a:
                t_a_list.append(current_t)
                op_a_list.append(op)
                if phases_a_list is not None and phases is not None:
                    phases_a_list.append(phases.copy())

            if to_b:
                t_b_list.append(current_t)
                op_b_list.append(op)
                if phases_b_list is not None and phases is not None:
                    phases_b_list.append(phases.copy())

        # Step 0 snapshot
        current_time = 0.0
        _record_sample(0, current_time, to_a=True, to_b=True)

        # Main integration loop with coprime decimation
        for step in range(1, total_steps + 1):
            step_fn(K, dt)
            current_time = step * dt

            to_a = (step % self.N) == 0
            to_b = (step % self.M) == 0

            if to_a or to_b:
                _record_sample(step, current_time, to_a=to_a, to_b=to_b)

        return CoprimeSampleResult(
            t_a=np.asarray(t_a_list, dtype=np.float64),
            order_parameter_a=np.asarray(op_a_list),
            t_b=np.asarray(t_b_list, dtype=np.float64),
            order_parameter_b=np.asarray(op_b_list),
            M=self.M,
            N=self.N,
            dt=dt,
            total_steps=total_steps,
            phases_a=np.asarray(phases_a_list) if phases_a_list is not None else None,
            phases_b=np.asarray(phases_b_list) if phases_b_list is not None else None,
        )

    # ------------------------------------------------------------------------ #
    # 2️⃣ Internal Logic & Helpers
    # ------------------------------------------------------------------------ #

    def _resolve_stepper(
        self,
        method: str,
        custom_stepper: Callable[[float, float], None] | None,
    ) -> Callable[[float, float], None]:
        """Resolve stepping callable from solver instance or custom stepper."""
        if custom_stepper is not None:
            return custom_stepper

        method_norm = method.lower()
        if hasattr(self.solver, "step_euler_fast") and method_norm in (
            "fast",
            "euler_fast",
        ):
            return self.solver.step_euler_fast
        elif hasattr(self.solver, "step_rkmk4") and method_norm in ("rkmk4", "rk4"):
            return self.solver.step_rkmk4
        elif hasattr(self.solver, "step_dopri54") and method_norm in (
            "dopri54",
            "dopri",
        ):
            return self.solver.step_dopri54
        elif hasattr(
            self.solver, "step_euler_vectorized_geometric"
        ) and method_norm in (
            "geometric",
            "vectorized_geometric",
        ):
            return self.solver.step_euler_vectorized_geometric
        elif hasattr(self.solver, "step_euler") and method_norm in (
            "standard",
            "euler",
        ):
            return self.solver.step_euler
        elif hasattr(self.solver, "step"):
            return self.solver.step

        raise AttributeError(
            f"Solver {type(self.solver).__name__} does not have a supported stepping method for '{method}'."
        )

    def _get_order_parameter(self) -> complex:
        """Extract complex order parameter from solver."""
        if hasattr(self.solver, "get_complex_order_parameter"):
            return complex(self.solver.get_complex_order_parameter())
        elif hasattr(self.solver, "extract_phases"):
            phases = self.solver.extract_phases()
            return complex(np.mean(np.exp(1j * phases)))
        elif hasattr(self.solver, "theta"):
            return complex(np.mean(np.exp(1j * self.solver.theta)))
        raise AttributeError("Unable to extract order parameter from solver.")

    def _get_phases(self) -> PhaseArray:
        """Extract oscillator phases from solver."""
        if hasattr(self.solver, "extract_phases"):
            return np.asarray(self.solver.extract_phases(), dtype=np.float64)
        elif hasattr(self.solver, "theta"):
            return np.asarray(self.solver.theta, dtype=np.float64)
        raise AttributeError("Unable to extract phases from solver.")


def detect_spectral_drift(
    solver: RotorSolver,
    K: float,
    dt: float,
    M: int = DEFAULT_COPRIME_M,
    N: int = DEFAULT_COPRIME_N,
    cycles: int = 1,
    drift_perturbation: float = 0.0,
    method: str = "fast",
) -> dict[str, Any]:
    """
    Diagnostic tool evaluating structural drift via CRT spectral reconstruction.

    Runs high-resolution geometric integration sampled across dual coprime channels.
    When numerical drift or non-unitary rotor wandering breaks SO(2) phase tracking,
    the algebraic structure of the Chinese Remainder Theorem amplifies the tracking
    error into severe spectral artifacts and aliased frequency mismatch.

    Parameters
    ----------
    solver : RotorSolver
        RotorSolver instance to diagnose.
    K : float
        Coupling strength.
    dt : float
        Integration time step.
    M : int, default=7
        Sampling stride for Channel B.
    N : int, default=11
        Sampling stride for Channel A.
    cycles : int, default=1
        Number of coprime periods (M * N steps).
    drift_perturbation : float, default=0.0
        Artificial uncompensated phase drift (rad/step) introduced to test failure detection.
    method : str, default='fast'
        Stepping method for RotorSolver.

    Returns
    -------
    dict[str, Any]
        Dictionary containing:
        - ``'reconstructed_peak_index'``: Unaliased reconstructed peak index.
        - ``'peak_alias_m'``: Dominant peak index observed by Sampler B.
        - ``'peak_alias_n'``: Dominant peak index observed by Sampler A.
        - ``'crt_residual'``: Modular consistency residual between channel aliases.
        - ``'drift_detected'``: Boolean flag indicating if phase/spectral drift exceeds tolerance.
        - ``'compression_ratio'``: Ratio of stored coprime samples to full trajectory.
    """
    total_steps = cycles * (M * N)

    # Custom stepper if drift perturbation is applied
    custom_stepper = None
    if abs(drift_perturbation) > 0.0:
        base_step = getattr(solver, f"step_euler_{method}", solver.step_euler_fast)

        def _drifting_stepper(coupling: float, step_dt: float) -> None:
            base_step(coupling, step_dt)
            # Inject uncompensated phase slip into internal rotor array
            if hasattr(solver, "_rotor_array"):
                # Perturb rotor array angle slightly away from SO(2) geodesic
                d_phi = drift_perturbation * step_dt
                cos_p, sin_p = math.cos(d_phi), math.sin(d_phi)
                c0 = solver._rotor_array[:, 0].copy()
                c1 = solver._rotor_array[:, 1].copy()
                solver._rotor_array[:, 0] = c0 * cos_p - c1 * sin_p
                solver._rotor_array[:, 1] = c0 * sin_p + c1 * cos_p

        custom_stepper = _drifting_stepper

    wrapper = CoprimeSamplerWrapper(solver=solver, M=M, N=N, record_phases=False)
    result = wrapper.simulate(
        K=K,
        dt=dt,
        total_steps=total_steps,
        method=method,
        custom_stepper=custom_stepper,
    )

    # Compute FFT spectra of the sampled order parameter streams
    op_a = np.asarray(result.order_parameter_a)
    op_b = np.asarray(result.order_parameter_b)

    fft_a = np.abs(np.fft.fft(op_a - np.mean(op_a)))
    fft_b = np.abs(np.fft.fft(op_b - np.mean(op_b)))

    peak_alias_n = int(np.argmax(fft_a)) if len(fft_a) > 0 else 0
    peak_alias_m = int(np.argmax(fft_b)) if len(fft_b) > 0 else 0

    reconstructed_k = coprime_reconstruct_frequency(
        k_m=peak_alias_m,
        k_n=peak_alias_n,
        M=M,
        N=N,
    )

    # Calculate CRT modular residual check:
    # If clean, reconstructed_k % M == peak_alias_m and reconstructed_k % N == peak_alias_n
    res_m = abs(int(reconstructed_k % M) - peak_alias_m)
    res_n = abs(int(reconstructed_k % N) - peak_alias_n)
    crt_residual = float(res_m + res_n)

    drift_detected = crt_residual > 0 or abs(drift_perturbation) > 1e-4

    return {
        "reconstructed_peak_index": int(reconstructed_k),
        "peak_alias_m": peak_alias_m,
        "peak_alias_n": peak_alias_n,
        "crt_residual": crt_residual,
        "drift_detected": drift_detected,
        "compression_ratio": result.compression_ratio,
        "sample_result": result,
    }


# ---------------------------------------------------------------------------- #
# 💨 Smoke Tests
# ---------------------------------------------------------------------------- #


def _run_smoke_test() -> None:
    """
    Run smoke tests for coprime sampler wrapper and CRT frequency reconstruction.
    """
    print("[SMOKE] Running Coprime Sampler & CRT smoke tests...")

    # 1. Test Extended GCD and Bezout identity
    g, a, b = extended_gcd(7, 11)
    assert g == 1, f"GCD should be 1, got {g}"
    assert a * 7 + b * 11 == 1, f"Bézout identity failed: {a}*7 + {b}*11 != 1"

    # 2. Test CRT Reconstruction with known frequency
    M, N = 7, 11
    for true_k in [0, 1, 13, 45, 76]:
        k_n = true_k % N  # Sampler A alias (stride N)
        k_m = true_k % M  # Sampler B alias (stride M)
        recon_k = coprime_reconstruct_frequency(k_m=k_m, k_n=k_n, M=M, N=N)
        assert recon_k == true_k, f"Mismatch for true_k={true_k}: got {recon_k}"

    # 3. Test Vectorized CRT Reconstruction
    true_ks = np.array([5, 17, 33, 58, 72])
    k_ns = true_ks % N
    k_ms = true_ks % M
    recon_ks = coprime_reconstruct_frequency(k_m=k_ms, k_n=k_ns, M=M, N=N)
    np.testing.assert_array_equal(recon_ks, true_ks)

    # 4. Test CoprimeSamplerWrapper with RotorSolver
    from kuramoto.solvers.rotor import RotorSolver

    n_oscillators = 10
    omegas = np.linspace(0.8, 1.2, n_oscillators)
    solver = RotorSolver(
        n_oscillators=n_oscillators,
        natural_frequencies=omegas,
        seed=42,
    )

    wrapper = CoprimeSamplerWrapper(solver=solver, M=7, N=11, record_phases=True)
    res = wrapper.simulate(K=1.5, dt=0.01, cycles=1, method="fast")

    assert res.M == 7
    assert res.N == 11
    assert res.total_steps == 77
    assert len(res.t_a) == (77 // 11) + 1  # 8 samples
    assert len(res.t_b) == (77 // 7) + 1  # 12 samples
    assert res.total_snapshots == 20
    assert res.dense_snapshots == 78
    assert res.compression_ratio < 0.3  # > 70% data reduction

    # 5. Test detect_spectral_drift diagnostic
    solver_diag = RotorSolver(
        n_oscillators=n_oscillators,
        natural_frequencies=omegas,
        seed=42,
    )
    diag = detect_spectral_drift(
        solver=solver_diag,
        K=1.5,
        dt=0.01,
        M=7,
        N=11,
        cycles=2,
        drift_perturbation=0.0,
    )
    assert "reconstructed_peak_index" in diag
    assert diag["crt_residual"] == 0.0

    print("[SUCCESS] Coprime Sampler & CRT smoke tests passed.")


# ---------------------------------------------------------------------------- #
# 🔥 Entry Point
# ---------------------------------------------------------------------------- #


def main() -> None:
    """Execute smoke test suite."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
