import numpy as np
import pytest

pytest.importorskip("clifford")

from kuramoto.order_parameter import compute_order_parameter
from kuramoto.solvers.rotor import RotorSolver, step_dopri54, step_rkmk4


def test_rotor_u1_invariance():
    """Verify global phase shift invariance in RotorSolver."""
    N = 10
    K = 1.0
    t_eval = np.linspace(0, 1.0, 11)
    dt = 0.01
    seed = 42

    # 1. Base simulation
    solver1 = RotorSolver(n_oscillators=N, seed=seed)
    _, phases1 = solver1.simulate(K=K, t_eval=t_eval, dt_internal=dt)
    r1 = compute_order_parameter(phases1)

    # 2. Shifted simulation
    solver2 = RotorSolver(n_oscillators=N, seed=seed)
    shift = 0.5 * np.pi
    B = solver2.B_plane
    # Shift initial state
    solver2.rotors = [r * np.exp(-B * shift / 2.0) for r in solver2.rotors]

    _, phases2 = solver2.simulate(K=K, t_eval=t_eval, dt_internal=dt)
    r2 = compute_order_parameter(phases2)

    # Order parameter magnitude should be invariant
    assert np.allclose(r1, r2, atol=1e-12)


def test_rotor_method_consistency():
    """Verify that 'fast', 'standard', and 'geometric' methods yield identical results."""
    N = 10
    K = 1.5
    t_eval = np.linspace(0, 0.5, 6)
    dt = 0.005
    seed = 123

    # Use 'fast' as reference
    solver_ref = RotorSolver(n_oscillators=N, seed=seed)
    _, phases_ref = solver_ref.simulate(
        K=K, t_eval=t_eval, dt_internal=dt, method="fast"
    )

    for method in ["standard", "geometric"]:
        solver = RotorSolver(n_oscillators=N, seed=seed)
        _, phases = solver.simulate(K=K, t_eval=t_eval, dt_internal=dt, method=method)
        assert np.allclose(phases_ref, phases, atol=1e-10)


def test_rotor_norm_preservation():
    """Verify that rotors remain normalized (magnitude 1) during evolution."""
    N = 5
    solver = RotorSolver(n_oscillators=N, seed=7)

    # Initial norms
    for r in solver.rotors:
        assert np.isclose(abs(r), 1.0, atol=1e-15)

    # Evolve
    solver.simulate(K=2.0, t_eval=np.linspace(0, 1.0, 5), dt_internal=0.01)

    # Final norms
    for r in solver.rotors:
        assert np.isclose(abs(r), 1.0, atol=1e-12)


def test_rotor_constructor_initial_conditions():
    """Verify direct injection of natural frequencies and initial phases in RotorSolver."""
    N = 4
    omegas = np.array([0.5, -0.2, 1.0, -1.0])
    phases = np.array([0.0, np.pi / 4, np.pi / 2, np.pi])

    solver = RotorSolver(
        n_oscillators=N,
        natural_frequencies=omegas,
        initial_phases=phases,
    )

    assert np.allclose(solver.omegas, omegas)
    extracted = solver.extract_phases()
    assert np.allclose(extracted, phases, atol=1e-12)


def test_rotor_nyquist_safe_adaptation_no_frequency_mutation():
    """Verify that enforce_nyquist adapts time step without mutating self.omegas."""
    import warnings

    N = 3
    large_omegas = np.array([50.0, 0.0, -50.0])
    solver = RotorSolver(n_oscillators=N, natural_frequencies=large_omegas)

    with warnings.catch_warnings(record=True) as recorded_warnings:
        warnings.simplefilter("always")
        solver.simulate(
            K=1.0,
            t_eval=np.linspace(0, 0.1, 5),
            dt_internal=0.05,
            enforce_nyquist=True,
        )
        assert any(
            "Temporal resolution warning" in str(w.message) for w in recorded_warnings
        )

    # Natural frequencies must remain unaltered
    assert np.allclose(solver.omegas, large_omegas)


def test_rotor_rkmk4_order_and_invariants():
    """Verify 4th-order Lie-group RKMK4 solver convergence and norm preservation."""
    N = 2
    omegas = np.array([0.0, 0.0])
    init_phases = np.array([0.0, np.pi / 3.0])
    K = 1.0

    solver_rkmk = RotorSolver(
        n_oscillators=N,
        natural_frequencies=omegas,
        initial_phases=init_phases,
    )

    t_eval = np.linspace(0, 0.5, 6)
    _, phases_rkmk = solver_rkmk.simulate(
        K=K,
        t_eval=t_eval,
        dt_internal=0.01,
        method="rkmk4",
    )

    # Exact 2-node ODE analytical solution: tan(Delta theta(t) / 2) = tan(Delta_0 / 2) * exp(-K * t)
    delta_0 = np.pi / 3.0
    exact_delta = 2.0 * np.arctan(np.tan(delta_0 / 2.0) * np.exp(-K * t_eval))
    simulated_delta = phases_rkmk[:, 1] - phases_rkmk[:, 0]

    assert np.allclose(simulated_delta, exact_delta, atol=1e-5)

    # Check rotor norm preservation in RKMK4
    for r in solver_rkmk.rotors:
        assert np.isclose(abs(r), 1.0, atol=1e-12)


def test_kuramoto_model_with_rkmk4():
    """Verify KuramotoModel works seamlessly with solver_type='rkmk4'."""
    from kuramoto.model import KuramotoModel

    model = KuramotoModel(
        n_oscillators=4,
        coupling_strength=1.5,
        random_seed=42,
        solver_type="rkmk4",
    )

    dataset = model.simulate(t_span=1.0, n_points=20)
    assert dataset.theta.shape == (20, 4)
    assert np.all(np.isfinite(dataset.theta))
    r = compute_order_parameter(dataset.theta)
    assert np.all(r >= 0.0)
    assert np.all(r <= 1.0 + 1e-6)


def test_step_rkmk4_standalone():
    """Verify that the standalone step_rkmk4 function integrates rotors properly."""
    N = 4
    solver = RotorSolver(n_oscillators=N, dim=2, seed=42)
    initial_rotors = solver._rotor_array.copy()

    updated_rotors = step_rkmk4(solver, K=1.0, dt=0.01)

    assert isinstance(updated_rotors, np.ndarray)
    assert updated_rotors.shape == (N, 2)
    assert np.allclose(solver._rotor_array, updated_rotors)
    assert not np.allclose(initial_rotors, updated_rotors)

    # Norms must stay equal to 1.0
    norms = np.sum(updated_rotors**2, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-12)


def test_step_dopri54_and_adaptive_invariants():
    """Verify Dormand-Prince 5(4) Lie-group stepper order, norm conservation, and time-reversibility."""
    N = 4
    solver = RotorSolver(n_oscillators=N, dim=2, seed=42)
    initial_rotors = solver._rotor_array.copy()

    # 1. Standalone step_dopri54
    updated_rotors = step_dopri54(solver, K=1.2, dt=0.01)
    assert isinstance(updated_rotors, np.ndarray)
    assert updated_rotors.shape == (N, 2)
    assert np.allclose(solver._rotor_array, updated_rotors)
    assert not np.allclose(initial_rotors, updated_rotors)

    # Norm conservation on Spin(2)
    norms = np.sum(updated_rotors**2, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-14)

    # 2. Time-reversal roundtrip over 10s
    solver_rev = RotorSolver(n_oscillators=6, dim=2, seed=123)
    init_phases = solver_rev.extract_phases()
    dt = 0.005
    n_steps = 200

    for _ in range(n_steps):
        step_dopri54(solver_rev, K=0.8, dt=dt)
    for _ in range(n_steps):
        step_dopri54(solver_rev, K=0.8, dt=-dt)

    recon_phases = solver_rev.extract_phases()
    recon_err = np.max(np.abs(np.exp(1j * recon_phases) - np.exp(1j * init_phases)))
    assert recon_err < 1e-12

    # 3. Full simulate with method='adaptive_dopri54'
    t_eval = np.linspace(0.0, 1.0, 11)
    solver_adapt = RotorSolver(n_oscillators=6, dim=2, seed=123)
    t_out, phases_out = solver_adapt.simulate(
        K=0.8, t_eval=t_eval, dt_internal=0.01, method="adaptive_dopri54"
    )
    assert len(t_out) == len(t_eval)
    assert phases_out.shape == (11, 6)
