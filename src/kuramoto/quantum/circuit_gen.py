# src/kuramoto/quantum/circuit_gen.py
"""
Quantum circuit generation for Kuramoto synchronization.

Implements the Self-Consistent Field (SCF) mapping to translate classical 
rotor dynamics into parallel quantum rotation gates with O(1) circuit depth.

Author: Eigenscribe & Junie
Date: 10-2026
"""

from __future__ import annotations
import numpy as np
from numpy.typing import NDArray
from typing import Dict, Any, List, Optional

def generate_scf_angles(
    phases: NDArray[np.floating],
    omegas: NDArray[np.floating],
    K: float,
    dt: float
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

    Returns
    -------
    NDArray
        Array of rotation angles phi_i for Rz gates.
    """
    # 1. Compute Mean Field (Order Parameter)
    v_mean = np.mean(np.exp(1j * phases))
    R = np.abs(v_mean)
    psi = np.angle(v_mean)

    # 2. Compute effective angular velocity (The SCF Torque)
    # dtheta/dt = omega + K*R*sin(psi - theta)
    dtheta_dt = omegas + K * R * np.sin(psi - phases)

    # 3. Map to gate angles (phi = velocity * dt)
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
    dataset: Dict[str, Any],
    step_idx: int = -1,
    dt: float = 0.05,
    K: float = 1.5,
) -> Dict[str, Any]:
    """
    High-level utility to synthesize a quantum circuit from a classical simulation snapshot.
    """
    phases = dataset["theta"][step_idx]
    omegas = dataset["omega"]
    
    angles = generate_scf_angles(phases, omegas, K, dt)
    qasm = export_to_qasm(angles)
    
    return {
        "n_qubits": len(phases),
        "angles": angles,
        "qasm": qasm,
        "depth": 1, # Always 1 for parallel Rz
        "mapping": "SCF-GA"
    }

if __name__ == "__main__":
    # Quick Smoke Test
    test_phases = np.array([0, 0.1, 0.2])
    test_omegas = np.ones(3)
    res = generate_scf_angles(test_phases, test_omegas, K=1.0, dt=0.01)
    print(f"Generated angles for N=3: {res}")
    print("\nSample QASM:")
    print(export_to_qasm(res))
