import numpy as np

from kuramoto.order_parameter import compute_order_parameter
from kuramoto.solvers.quantum_rotor import QuantumRotorSolver, step_quantum_scf


def test_quantum_rotor_solver_initialization():
    """Verify solver initialization, defaults, and custom states."""
    solver = QuantumRotorSolver(n_oscillators=8, seed=42)
    assert solver.N == 8
    assert len(solver.phases) == 8
    assert len(solver.omegas) == 8
    assert np.all((solver.phases >= -np.pi) & (solver.phases <= np.pi))


def test_quantum_rotor_schemes_equivalence():
    """Verify that statevector and expectation schemes produce identical trajectories."""
    t_eval = np.linspace(0.0, 2.0, 20)
    seed = 123
    n_oscillators = 10
    K = 1.2

    solver1 = QuantumRotorSolver(n_oscillators=n_oscillators, seed=seed)
    _, traj1 = solver1.simulate(K=K, t_eval=t_eval, scheme="statevector")

    solver2 = QuantumRotorSolver(n_oscillators=n_oscillators, seed=seed)
    _, traj2 = solver2.simulate(K=K, t_eval=t_eval, scheme="expectation")

    assert np.allclose(traj1, traj2, atol=1e-5)


def test_quantum_rotor_order_parameter_bounds():
    """Verify order parameter r(t) bounds [0, 1] during quantum SCF simulation."""
    solver = QuantumRotorSolver(n_oscillators=15, seed=99)
    t_eval = np.linspace(0.0, 5.0, 30)
    _, traj = solver.simulate(K=2.0, t_eval=t_eval, scheme="statevector")

    r = compute_order_parameter(traj)
    assert r.shape == (30,)
    assert np.all((r >= 0.0) & (r <= 1.0 + 1e-6))


def test_quantum_rotor_shot_sampling_statistical_convergence():
    """Verify that shot_sampling approaches statevector as shot count increases."""
    phases = np.array([0.1, -0.4, 0.8, -1.2])
    omegas = np.array([0.5, 0.5, -0.5, -0.5])
    K = 1.0
    dt = 0.05

    exact_next = step_quantum_scf(phases, omegas, K=K, dt=dt, scheme="statevector")

    # High shot count should be close to exact
    sampled_next_high = step_quantum_scf(
        phases,
        omegas,
        K=K,
        dt=dt,
        scheme="shot_sampling",
        shots=100000,
        rng=np.random.default_rng(42),
    )
    assert np.allclose(exact_next, sampled_next_high, atol=0.03)


def test_quantum_rotor_qasm_generation():
    """Verify OpenQASM export from quantum solver instance."""
    solver = QuantumRotorSolver(n_oscillators=4, seed=42)
    qasm = solver.to_qasm(K=1.0, dt=0.01)

    assert "OPENQASM 2.0;" in qasm
    assert "qreg q[4];" in qasm
    assert "rz(" in qasm


def test_quantum_rotor_with_topology_adjacency():
    """Verify quantum solver execution with adjacency matrices from kuramoto.topologies."""
    from kuramoto.topologies import load_topology

    n = 6
    adj_ring = load_topology("ring", n=n)
    adj_sw = load_topology("small_world", n=n, k=2, p=0.1)
    adj_bip = load_topology("bipartite", n=n)

    for adj in (adj_ring, adj_sw, adj_bip):
        solver = QuantumRotorSolver(n_oscillators=n, seed=42, adjacency_matrix=adj)
        assert solver.adjacency_matrix is not None
        assert solver.adjacency_matrix.shape == (n, n)

        t_eval = np.linspace(0.0, 1.0, 10)
        t_out, traj = solver.simulate(K=1.5, t_eval=t_eval, scheme="statevector")
        assert traj.shape == (10, n)
        r = compute_order_parameter(traj)
        assert np.all((r >= 0.0) & (r <= 1.0 + 1e-6))


def test_quantum_rotor_matches_euler_with_adjacency():
    """Verify that quantum statevector step exactly matches Euler graph coupling."""
    from kuramoto.topologies import load_topology

    n = 8
    adj = load_topology("ring", n=n)
    phases = np.array([0.1, -0.5, 0.8, -1.2, 0.4, -0.9, 1.1, -0.2])
    omegas = np.array([0.5, -0.3, 0.2, -0.4, 0.1, 0.6, -0.5, 0.3])
    K = 1.4
    dt = 0.02

    # Classical Euler step on graph A
    diff = phases[np.newaxis, :] - phases[:, np.newaxis]
    coupling = (K / n) * np.sum(adj * np.sin(diff), axis=1)
    euler_next = (phases + dt * (omegas + coupling) + np.pi) % (2 * np.pi) - np.pi

    # Quantum statevector step with adjacency
    quantum_next = step_quantum_scf(
        phases, omegas, K=K, dt=dt, adjacency_matrix=adj, scheme="statevector"
    )

    assert np.allclose(euler_next, quantum_next, atol=1e-12)


def test_quantum_rotor_k0_decoupled_drift():
    """Verify that K=0 evolves strictly as exact decoupled phase drift."""
    n_oscillators = 10
    seed = 42
    K = 0.0
    t_eval = np.linspace(0.0, 5.0, 50)

    solver_sv = QuantumRotorSolver(n_oscillators=n_oscillators, seed=seed)
    theta0 = solver_sv.phases.copy()
    omegas = solver_sv.omegas.copy()

    solver_exp = QuantumRotorSolver(
        n_oscillators=n_oscillators,
        seed=seed,
        initial_phases=theta0,
        natural_frequencies=omegas,
    )

    _, traj_sv = solver_sv.simulate(K=K, t_eval=t_eval, scheme="statevector")
    _, traj_exp = solver_exp.simulate(K=K, t_eval=t_eval, scheme="expectation")

    # Analytical exact phase trajectory: (theta0 + omega * t + pi) % (2pi) - pi
    exact_traj = (theta0[None, :] + omegas[None, :] * t_eval[:, None] + np.pi) % (
        2.0 * np.pi
    ) - np.pi

    # Compare chordal / circular distance to handle boundary wrapping at +/- pi
    diff_sv = np.abs(np.exp(1j * traj_sv) - np.exp(1j * exact_traj))
    diff_exp = np.abs(np.exp(1j * traj_exp) - np.exp(1j * exact_traj))

    assert np.all(diff_sv < 1e-12)
    assert np.all(diff_exp < 1e-12)


def test_quantum_rotor_unitary_time_reversal():
    """Verify exact unitary gate adjoint invertibility and K=0 step reversibility."""
    n_oscillators = 8
    seed = 2026
    K = 1.5
    dt = 0.01
    n_steps = 50

    rng = np.random.default_rng(seed)
    phases_init = rng.uniform(-np.pi, np.pi, size=n_oscillators)
    omegas = rng.normal(0.0, 1.0, size=n_oscillators)

    # 1. Forward unitary evolution: record rotation angles applied at each step
    angle_history: list[np.ndarray] = []
    phases_curr = phases_init.copy()
    for _ in range(n_steps):
        from kuramoto.quantum.circuit_gen import generate_scf_angles

        phi = generate_scf_angles(phases_curr, omegas, K=K, dt=dt)
        angle_history.append(phi)
        phases_curr = (phases_curr + phi + np.pi) % (2.0 * np.pi) - np.pi

    # 2. Exact unitary inversion via adjoint rotations in reverse sequence: U_dagger = prod R_Z(-phi_k)
    phases_recon = phases_curr.copy()
    for phi in reversed(angle_history):
        phases_recon = (phases_recon - phi + np.pi) % (2.0 * np.pi) - np.pi

    recon_error = np.abs(np.exp(1j * phases_recon) - np.exp(1j * phases_init))
    assert np.all(recon_error < 1e-12)

    # 3. K=0 decoupled time-reversal with -dt directly
    phases_k0 = phases_init.copy()
    for _ in range(n_steps):
        phases_k0 = step_quantum_scf(phases_k0, omegas, K=0.0, dt=dt, scheme="statevector")
    for _ in range(n_steps):
        phases_k0 = step_quantum_scf(phases_k0, omegas, K=0.0, dt=-dt, scheme="statevector")

    recon_error_k0 = np.abs(np.exp(1j * phases_k0) - np.exp(1j * phases_init))
    assert np.all(recon_error_k0 < 1e-12)


def test_quantum_rotor_u1_gauge_invariance():
    """Verify SO(2) / U(1) global gauge equivariance and invariant order parameter."""
    n_oscillators = 12
    seed = 77
    K = 1.8
    t_eval = np.linspace(0.0, 3.0, 30)
    alpha = 1.234  # arbitrary global phase shift

    solver1 = QuantumRotorSolver(n_oscillators=n_oscillators, seed=seed)
    solver2 = QuantumRotorSolver(
        n_oscillators=n_oscillators,
        seed=seed,
        initial_phases=solver1.phases + alpha,
        natural_frequencies=solver1.omegas,
    )

    _, traj1 = solver1.simulate(K=K, t_eval=t_eval, scheme="statevector")
    _, traj2 = solver2.simulate(K=K, t_eval=t_eval, scheme="statevector")

    # Order parameters must be identical down to machine precision
    r1 = compute_order_parameter(traj1)
    r2 = compute_order_parameter(traj2)
    assert np.allclose(r1, r2, atol=1e-12)

    # Rotated trajectory must match original shifted by alpha
    expected_traj2 = (traj1 + alpha + np.pi) % (2.0 * np.pi) - np.pi
    diff = np.abs(np.exp(1j * traj2) - np.exp(1j * expected_traj2))
    assert np.all(diff < 1e-12)
