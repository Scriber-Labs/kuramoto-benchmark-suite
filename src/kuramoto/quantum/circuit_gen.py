"""
kuramoto.quantum.circuit_gen

Quantum circuit generation for Kuramoto synchronization.

Implements the Self-Consistent Field (SCF) mapping to translate classical
rotor dynamics into parallel quantum rotation gates with O(1) circuit depth.

Author: Eigenscribe
Date: November 2026
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Core definitions
# -----------------------------------------------------------------------------------------------------------


def generate_scf_angles(
    phases: NDArray[np.floating],
    omegas: NDArray[np.floating],
    K: float,
    dt: float,
    adjacency_matrix: NDArray[np.floating] | None = None,
) -> NDArray[np.floating]:
    """
    Compute parallel Rz gate angles using the Self-Consistent Field (SCF) mapping.

    This maps the non-linear interaction to a time-dependent mean field,
    allowing N oscillators to be updated in parallel.

    Parameters
    ----------
    phases : NDArray
        Current oscillator phases (theta_i).
    omegas : NDArray
        Natural frequencies (omega_i).
    K : float
        Coupling strength.
    dt : float
        Integration timestep.
    adjacency_matrix : NDArray, optional
        Adjacency matrix of shape (N, N) defining the network topology.

    Returns
    -------
    NDArray
        Array of rotation angles phi_i for Rz gates.
    """
    z = np.exp(1j * phases)
    if adjacency_matrix is not None:
        # 1. Compute Local Mean Field via Adjacency Matrix
        v_local = (adjacency_matrix @ z) / len(phases)
        R = np.abs(v_local)
        psi = np.angle(v_local)
        dtheta_dt = omegas + K * R * np.sin(psi - phases)
    else:
        # 1. Compute Global Mean Field (Order Parameter)
        v_mean = np.mean(z)
        R = np.abs(v_mean)
        psi = np.angle(v_mean)
        dtheta_dt = omegas + K * R * np.sin(psi - phases)

    # 2. Map to gate angles (phi = velocity * dt)
    return dtheta_dt * dt


def export_to_qasm(angles: NDArray[np.floating]) -> str:
    """
    Generate an OpenQASM 2.0 representation of the parallel synchronization update.

    Parameters
    ----------
    angles : NDArray
        Array of Rz rotation angles.

    Returns
    -------
    str
        QASM source code.
    """
    N = len(angles)
    qasm = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{N}];",
        "",
        "// Parallel Synchronization Update (O(1) Depth)",
    ]
    for i, phi in enumerate(angles):
        qasm.append(f"rz({phi:.6f}) q[{i}];")
    return "\n".join(qasm)


def synthesize_quantum_bridge(
    dataset: dict[str, Any],
    step_idx: int = -1,
    dt: float = 0.05,
    K: float = 1.5,
    adjacency_matrix: NDArray[np.floating] | None = None,
) -> dict[str, Any]:
    """
    High-level utility to synthesize a quantum circuit from a classical simulation snapshot.
    """
    phases = dataset["theta"][step_idx]
    omegas = dataset["omega"]
    adj = (
        adjacency_matrix
        if adjacency_matrix is not None
        else dataset.get("adjacency_matrix")
    )

    angles = generate_scf_angles(phases, omegas, K, dt, adjacency_matrix=adj)
    qasm = export_to_qasm(angles)

    return {
        "n_qubits": len(phases),
        "angles": angles,
        "qasm": qasm,
        "depth": 1,  # Always 1 for parallel Rz
        "mapping": "SCF-GA",
    }


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for quantum circuit generation."""
    test_phases = np.array([0.0, 0.1, 0.2])
    test_omegas = np.ones(3)
    test_adj = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=float)

    # Test SCF angle generation
    res = generate_scf_angles(test_phases, test_omegas, K=1.0, dt=0.01)
    assert res.shape == (3,), f"Expected shape (3,), got {res.shape}"

    res_adj = generate_scf_angles(
        test_phases, test_omegas, K=1.0, dt=0.01, adjacency_matrix=test_adj
    )
    assert res_adj.shape == (3,)

    # Test QASM export
    qasm = export_to_qasm(res)
    assert "OPENQASM 2.0;" in qasm
    assert "qreg q[3];" in qasm
    assert "rz(" in qasm

    # Test quantum bridge synthesis
    dataset = {
        "theta": np.array([[0.0, 0.1, 0.2], [0.05, 0.15, 0.25]]),
        "omega": np.ones(3),
    }
    bridge = synthesize_quantum_bridge(dataset, step_idx=0, dt=0.01, K=1.0)
    assert bridge["n_qubits"] == 3
    assert bridge["depth"] == 1
    assert "qasm" in bridge

    print("✅ Quantum circuit_gen smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Entry point for module-level smoke testing."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
