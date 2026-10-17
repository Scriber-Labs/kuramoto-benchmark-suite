# src/kuramoto/solvers/quantum_rotor_bridge.py
from __future__ import annotations
import numpy as np
from kuramoto.solvers.rotor import RotorSolver
from kuramoto.solvers.quantum_rk45 import QuantumRK45Solver


class QuantumRotorAdaptiveSolver(RotorSolver):
    """
    Subclass of RotorSolver overriding fixed-step Euler with a
    Quantum Phase adaptive RK45 engine.
    """

    def simulate_quantum_rk45(
            self,
            K: float,
            t_start: float,
            t_end: float,
            initial_dt: float = 0.05,
            atol: float = 1e-5
    ) -> list[complex]:
        """ Runs adaptive RK45 simulation natively utilizing Qiskit primitives """
        # Bind the Qiskit engine backend
        quantum_engine = QuantumRK45Solver(self.omegas, K)

        t = t_start
        dt = initial_dt
        order_parameters = []

        # Pull geometric algebra starting phases
        current_phases = self.extract_phases()

        while t < t_end:
            # Advance utilizing our hybrid co-processor function
            next_phases, next_dt, accepted = quantum_engine.adaptive_step(current_phases, dt, atol=atol)

            if accepted:
                current_phases = next_phases
                t += dt
                # Update back into internal GA geometric rotors format
                self.rotors = [np.exp(-self.B_plane * p / 2.0) for p in current_phases]
                order_parameters.append(self.get_complex_order_parameter())

            dt = next_dt
            if dt < 1e-6:
                raise RuntimeError("Simulation halted: Time step shrank below practical threshold.")

        return order_parameters


# --- Practical Usage Verification ---
if __name__ == "__main__":
    # Initialize your 10 oscillator model
    solver = QuantumRotorAdaptiveSolver(n_oscillators=10, dim=2, seed=42)

    print("Initial sync value:", solver.get_synchronization_strength())
    print("Evolving system via adaptive Quantum-RK45 loops...")

    sync_profile = solver.simulate_quantum_rk45(K=2.5, t_start=0.0, t_end=2.0)
    print("Final synchronized value reached:", solver.get_synchronization_strength())
