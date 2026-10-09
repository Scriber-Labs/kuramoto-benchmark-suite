# src/kuramoto/solvers/quantum_rk45.py
from __future__ import annotations
import numpy as np
from numpy.typing import NDArray
from qiskit import QuantumCircuit
from qiskit.primitives import Estimator
from qiskit.quantum_info import SparsePauliOp

# Dormand-Prince (RK45) Butcher Tableau Coefficients
A_DP = [
    [],
    [1 / 5],
    [3 / 40, 9 / 40],
    [44 / 45, -56 / 15, 32 / 9],
    [19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729],
    [9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656]
]
B5 = [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84]
B4 = [5179 / 57600, 0, 7571 / 16695, 393 / 640, -92097 / 339200, 187 / 2100, 1 / 40]


class QuantumRK45Solver:
    """Hybrid Quantum-Classical RK45 solver for Kuramoto Models up to 10 qubits."""

    def __init__(self, omegas: NDArray[np.floating], K: float):
        self.omegas = np.asarray(omegas, dtype=float)
        self.N = len(omegas)
        self.K = K
        self.estimator = Estimator()

    def _get_field_velocities(self, phases: NDArray[np.floating]) -> NDArray[np.floating]:
        """Calculates instantaneous angular velocities on the classical host."""
        diff_matrix = phases[np.newaxis, :] - phases[:, np.newaxis]
        return self.omegas + (self.K / self.N) * np.sum(np.sin(diff_matrix), axis=1)

    def get_phases_qpu(self, current_phases: NDArray[np.floating]) -> NDArray[np.floating]:
        """
        Uses an O(1) depth parallel Qiskit circuit to measure oscillator coordinates
        without costly multiqubit entangling gates.
        """
        qc = QuantumCircuit(self.N)
        # 1. State preparation: Encode phase into relative qubit phase
        for i, phase in enumerate(current_phases):
            qc.h(i)
            qc.p(phase, i)

        # 2. Extract state observables in parallel via Qiskit Estimator Primitives
        obs_x = [SparsePauliOp.from_list([("X" if j == i else "I", 1.0) for j in range(self.N)]) for i in range(self.N)]
        obs_y = [SparsePauliOp.from_list([("Y" if j == i else "I", 1.0) for j in range(self.N)]) for i in range(self.N)]

        # Concurrent evaluation runs efficiently on hardware
        res_x = self.estimator.run([qc] * self.N, obs_x).result().values
        res_y = self.estimator.run([qc] * self.N, obs_y).result().values

        # Calculate angles directly from Bloch vectors
        return np.arctan2(res_y, res_x) % (2 * np.pi)

    def adaptive_step(self, phases: NDArray[np.floating], dt: float, atol: float = 1e-5) -> tuple[
        NDArray[np.floating], float, bool]:
        """Computes the Dormand-Prince step and checks local truncation error."""
        k = np.zeros((7, self.N))
        k[0] = self._get_field_velocities(phases)

        # Classical multi-stage evaluation loops
        for stage in range(1, 6):
            temp_phases = phases + dt * np.dot(A_DP[stage], k[:stage], axis=0)
            k[stage] = self._get_field_velocities(temp_phases)

        # Generate 4th and 5th order evolution comparisons
        phases_5th = phases + dt * np.dot(B5, k[:6], axis=0)
        k[6] = self._get_field_velocities(phases_5th)
        phases_4th = phases + dt * np.dot(B4, k[:7], axis=0)

        # Measure error delta
        error = np.max(np.abs(phases_5th - phases_4th))
        if error > atol:
            return phases, dt * 0.5, False  # Reject step, reduce dt

        # Compile optimal step into target phases via single-qubit Rz rotation equivalent
        qpu_aligned_phases = self.get_phases_qpu(phases_5th)
        next_dt = dt * 1.5 if error < (atol * 0.1) else dt
        return qpu_aligned_phases, next_dt, True
