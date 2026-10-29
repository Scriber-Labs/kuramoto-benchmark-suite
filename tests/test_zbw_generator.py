"""Tests for kuramoto.models.zbw_generator — ZBW Kuramoto Data Generator."""

from __future__ import annotations

import numpy as np

from kuramoto.models import ZBWKuramotoDataGenerator
from kuramoto.models.zbw_generator import GOLDEN_RATIO, _build_coprime_adjacency


class TestInitialization:
    """Tests for ZBWKuramotoDataGenerator.__init__."""

    def test_default_parameters(self) -> None:
        """Default constructor creates valid instance."""
        gen = ZBWKuramotoDataGenerator()
        assert gen.N == 100
        assert gen.omega_0 == 1.0
        assert gen.K == 0.5

    def test_custom_parameters(self) -> None:
        """Custom parameters are stored correctly."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=50, omega_0=2.0, coupling_K=1.5)
        assert gen.N == 50
        assert gen.omega_0 == 2.0
        assert gen.K == 1.5

    def test_phi_equals_golden_ratio(self) -> None:
        """Golden ratio constant matches module-level GOLDEN_RATIO."""
        gen = ZBWKuramotoDataGenerator()
        assert gen.phi == GOLDEN_RATIO
        assert abs(gen.phi - (1.0 + np.sqrt(5.0)) / 2.0) < 1e-15

    def test_frequency_shapes(self) -> None:
        """Intrinsic frequencies array has correct shape."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=30)
        assert gen.intrinsic_frequencies.shape == (30,)

    def test_frequencies_strictly_increasing(self) -> None:
        """Phi-shield frequencies are strictly increasing."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=20)
        diffs = np.diff(gen.intrinsic_frequencies)
        assert np.all(diffs > 0)

    def test_frequency_scaling_with_omega_0(self) -> None:
        """Frequencies scale linearly with omega_0."""
        gen1 = ZBWKuramotoDataGenerator(num_oscillators=10, omega_0=1.0)
        gen2 = ZBWKuramotoDataGenerator(num_oscillators=10, omega_0=3.0)
        assert np.allclose(gen2.intrinsic_frequencies, gen1.intrinsic_frequencies * 3.0)


class TestCoprimeAdjacency:
    """Tests for coprime adjacency matrix construction."""

    def test_adjacency_shape(self) -> None:
        """Adjacency matrix is N x N."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=15)
        assert gen.adjacency_matrix.shape == (15, 15)

    def test_adjacency_symmetric(self) -> None:
        """Adjacency matrix is symmetric."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=20)
        assert np.allclose(gen.adjacency_matrix, gen.adjacency_matrix.T)

    def test_adjacency_zero_diagonal(self) -> None:
        """No self-loops: diagonal is all zeros."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=20)
        assert np.all(np.diag(gen.adjacency_matrix) == 0.0)

    def test_adjacency_binary(self) -> None:
        """Adjacency entries are 0 or 1."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=20)
        unique_vals = np.unique(gen.adjacency_matrix)
        assert set(unique_vals).issubset({0.0, 1.0})

    def test_coprime_logic_small(self) -> None:
        """Verify coprime connections for small N."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=5)
        adj = gen.adjacency_matrix
        # Node 0 (index 1) and node 1 (index 2): gcd(1,2)=1 -> connected
        assert adj[0, 1] == 1.0
        # Node 0 (index 1) and node 3 (index 4): gcd(1,4)=1 -> connected
        assert adj[0, 3] == 1.0
        # Node 1 (index 2) and node 3 (index 4): gcd(2,4)=2 -> NOT connected
        assert adj[1, 3] == 0.0

    def test_build_coprime_adjacency_helper(self) -> None:
        """Private helper produces symmetric zero-diagonal matrix."""
        adj = _build_coprime_adjacency(10)
        assert adj.shape == (10, 10)
        assert np.allclose(adj, adj.T)
        assert np.all(np.diag(adj) == 0.0)


class TestCouplingMatrix:
    """Tests for coupling matrix scaling."""

    def test_coupling_shape(self) -> None:
        """Coupling matrix matches adjacency shape."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=25)
        assert gen.coupling_matrix.shape == (25, 25)

    def test_coupling_scaling(self) -> None:
        """Coupling matrix equals K/N * adjacency."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=10, coupling_K=2.0)
        expected = (gen.K / gen.N) * gen.adjacency_matrix
        assert np.allclose(gen.coupling_matrix, expected)


class TestPhaseEvolutionDerivatives:
    """Tests for phase_evolution_derivatives method."""

    def test_output_shape(self) -> None:
        """Derivatives output matches input phase shape."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=12)
        phases = np.random.uniform(0, 2 * np.pi, 12)
        dtheta = gen.phase_evolution_derivatives(time=0.0, phases=phases)
        assert dtheta.shape == (12,)

    def test_zero_coupling_isolates_oscillators(self) -> None:
        """With K=0, derivatives equal intrinsic frequencies plus LED torque."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=5, coupling_K=0.0)
        phases = np.zeros(5)
        dtheta = gen.phase_evolution_derivatives(
            time=0.0, phases=phases, led_amplitude=0.0
        )
        # At t=0, LED torque is 0; with K=0, only intrinsic frequencies remain
        assert np.allclose(dtheta, gen.intrinsic_frequencies)

    def test_led_torque_effect(self) -> None:
        """LED torque modifies derivatives at nonzero time."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=5, coupling_K=0.0)
        phases = np.zeros(5)
        dtheta_no_led = gen.phase_evolution_derivatives(
            time=0.0, phases=phases, led_amplitude=0.0
        )
        dtheta_with_led = gen.phase_evolution_derivatives(
            time=0.1, phases=phases, led_amplitude=2.0, led_frequency=60.0
        )
        # At t=0.1, LED torque should differ from t=0
        assert not np.allclose(dtheta_no_led, dtheta_with_led)

    def test_deterministic_output(self) -> None:
        """Same inputs produce identical outputs."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=10, coupling_K=0.8)
        phases = np.random.default_rng(42).uniform(0, 2 * np.pi, 10)
        dtheta1 = gen.phase_evolution_derivatives(time=1.0, phases=phases)
        dtheta2 = gen.phase_evolution_derivatives(time=1.0, phases=phases)
        assert np.allclose(dtheta1, dtheta2)


class TestOrderParameter:
    """Tests for compute_order_parameter method."""

    def test_perfect_sync(self) -> None:
        """All phases equal gives r=1."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=10)
        phases = np.zeros(10)
        z = gen.compute_order_parameter(phases)
        assert abs(abs(z) - 1.0) < 1e-12

    def test_incoherent_state(self) -> None:
        """Uniformly distributed phases give r near 0."""
        rng = np.random.default_rng(42)
        gen = ZBWKuramotoDataGenerator(num_oscillators=1000)
        phases = rng.uniform(0, 2 * np.pi, 1000)
        z = gen.compute_order_parameter(phases)
        # Law of large numbers: r should be small
        assert abs(z) < 0.1

    def test_order_parameter_bounds(self) -> None:
        """Order parameter magnitude is always in [0, 1]."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=50)
        rng = np.random.default_rng(123)
        for _ in range(10):
            phases = rng.uniform(0, 2 * np.pi, 50)
            z = gen.compute_order_parameter(phases)
            r = abs(z)
            assert 0.0 <= r <= 1.0 + 1e-6

    def test_phase_shift_invariance(self) -> None:
        """Shifting all phases by constant preserves r magnitude."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=20)
        rng = np.random.default_rng(42)
        phases = rng.uniform(0, 2 * np.pi, 20)
        z1 = gen.compute_order_parameter(phases)
        shifted = phases + np.pi / 4
        z2 = gen.compute_order_parameter(shifted)
        assert abs(abs(z1) - abs(z2)) < 1e-12


class TestEdgeCases:
    """Edge case and boundary tests."""

    def test_single_oscillator(self) -> None:
        """Single oscillator: no coupling, order parameter is 1."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=1)
        assert gen.adjacency_matrix.shape == (1, 1)
        assert np.all(gen.adjacency_matrix == 0.0)
        phases = np.array([0.5])
        z = gen.compute_order_parameter(phases)
        assert abs(abs(z) - 1.0) < 1e-12

    def test_two_oscillators(self) -> None:
        """Two oscillators: gcd(1, 2) = 1, so they connect."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=2)
        assert gen.adjacency_matrix[0, 1] == 1.0
        assert gen.adjacency_matrix[1, 0] == 1.0

    def test_large_ensemble(self) -> None:
        """Large ensemble initializes without error."""
        gen = ZBWKuramotoDataGenerator(num_oscillators=200)
        assert gen.N == 200
        phases = np.random.uniform(0, 2 * np.pi, 200)
        dtheta = gen.phase_evolution_derivatives(time=0.0, phases=phases)
        assert dtheta.shape == (200,)
