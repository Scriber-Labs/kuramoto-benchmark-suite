# 💫 Kuramoto Benchmark Suite

A research-grade synthetic dataset generator, Clifford Geometric Algebra rotor integrator, hybrid Quantum SCF simulator, and diagnostic suite for coupled oscillator systems.

This repository provides a modular, CLI-driven framework for simulating Kuramoto dynamics and performing spectral, topological, Lie-algebraic, and quantum circuit analysis. Designed with a "What -> Who -> How -> Proof" narrative flow conforming to Scriber Core standards.

**✨ Key Features & Recent Additions (v0.4, Oct 2026)**
- 🌀 **Geometric Algebra Rotor Solvers:** $\operatorname{Cl}_{2,0}(\mathbb{R})$ even-subalgebra multivector representation with high-order Runge-Kutta-Munthe-Kaas (`rkmk4`), embedded adaptive Dormand-Prince (`dopri54`), geometric midpoint, predictor-corrector (`pc`), and fast vectorized Euler integrators.
- ⚛️ **Hybrid Quantum Rotor Solver (Quantum SCF):** Map oscillator phases to single-qubit Bloch equatorial states $|q_j(t)\rangle = R_Z(\theta_j)|+\rangle$ evolved via self-consistent field (SCF) unitary rotations $U(t) = \bigotimes_j R_Z(\phi_j^{(t)})$, supporting `statevector`, `expectation`, and tomography `shot_sampling` simulation schemes.
- 🔌 **OpenQASM 2.0 / 3.0 Circuit Export:** Generate and export production-ready quantum circuits directly from simulation trajectories or CLI commands.
- 🔗 **Lie Symmetry & Gauge Invariants:** Exact $U(1) \cong \operatorname{SO}(2)$ phase shift equivariance, rotor norm conservation ($\|R_j\|=1.0$), and Noether energy/Hamiltonian drift diagnostics.
- 📊 **Spectral Diagnostics & Visualization:** Synchronization transition detection ($K_c$), harmonic cascades, PSD variability, Fourier convergence, and degree-preserving color themes.
- 🛠️ **Unified CLI Suite:** Dedicated commands for simulation (`generate`), hybrid quantum execution (`quantum`), circuit export (`qasm`), runtime/accuracy benchmarks (`benchmark`), and diagnostic plots (`network`, `time`, `fouriervariability`, `psdvariability`, etc.).

---

## 🚀 Quickstart

### Installation
```bash
git clone https://github.com/yourusername/kuramoto-benchmark-suite.git
cd kuramoto-benchmark-suite
pip install -e ".[dev]"
```

Or using `uv`:
```bash
uv sync --extra dev
```

### Core & Optional Dependencies
- **Core Simulation**: `numpy>=1.23`, `scipy>=1.10`, `networkx>=3.0`, `matplotlib>=3.5`, `seaborn>=0.12`, `tabulate>=0.9`, `click>=8.0`, `sympy>=1.12`
- **Geometric Algebra**: `clifford>=1.5.1` (required for $\operatorname{Cl}_{2,0}(\mathbb{R})$ bivector multivector rotor operations)
- **Quantum Integration**: Standard numerical backends built-in; OpenQASM export ready for Qiskit, Cirq, AWS Braket, and PennyLane.

---

## 🔰 CLI Usage & Examples

The `kuramoto` command line interface provides complete access to simulation, quantum execution, benchmarking, and visualization tools.

### Diagnostic & Simulation Commands

| **Command** | **Description** |
|:------------|:----------------|
| `generate` | Generate Kuramoto datasets across ODE, GA rotor, or Quantum solvers *(JSON or CLI flags)* |
| `quantum` | Run hybrid Quantum Self-Consistent Field (SCF) rotor simulation |
| `qasm` | Export single-step or multi-step Quantum SCF circuits to OpenQASM 2.0/3.0 |
| `benchmark` | Run comparative runtime and order parameter performance benchmarks across solvers |
| `datasetforbeginners` | Copy or generate a starter demo dataset to quickly explore the suite |
| `network` | Visualize graph topology with degree-based palette coloring |
| `distributions` | Plot natural frequency and initial phase distributions |
| `time` | Plot phase trajectories and global order parameter $r(t)$ |
| `fouriervariability` | Inspect Fourier coefficients at a target frequency |
| `fourierconvergence` | Plot Fourier amplitude convergence over increasing window lengths |
| `psdvariability` | Analyze Power Spectral Density (PSD) and energy distribution |
| `psdconvergence` | Compare PSD estimates across multiple time segments |

---

### CLI Command Highlights

#### 1. Dataset Generation (`kuramoto generate`)
```bash
# Standard adaptive Runge-Kutta (Classical RK45)
kuramoto generate -n 25 -K 1.5 -t 1000 --dt 0.05 --solver rk45 -o data/rk45.npz

# 4th-Order Lie-group Geometric Algebra Rotor (RKMK4)
kuramoto generate -n 50 -K 2.0 -t 500 --dt 0.01 --solver rkmk4 --track-symmetries -o data/rotor_rkmk4.npz

# Embedded Adaptive Geometric Algebra Rotor (DOPRI54) with custom error tolerances
kuramoto generate -n 30 -K 1.8 -t 1000 --solver dopri54 --adaptive-rtol 1e-6 --adaptive-atol 1e-8 -o data/rotor_adaptive.npz

# Quantum SCF solver (Statevector scheme) with QASM export
kuramoto generate -n 12 -K 1.5 -t 200 --dt 0.02 --solver quantum --scheme statevector --qasm-out data/circuit.qasm -o data/quantum.npz

# Stochastic shot-sampling quantum solver (Tomography shot noise)
kuramoto generate -n 16 -K 1.2 -t 300 --dt 0.02 --solver shot_sampling --shots 2048 -o data/quantum_shots.npz
```

#### 2. Direct Quantum Simulation (`kuramoto quantum`)
```bash
# Run 10-qubit Quantum SCF simulation in expectation mode
kuramoto quantum -n 10 -K 1.5 -t 200 --dt 0.02 --scheme expectation

# Run shot-sampling tomography simulation on a Ring topology
kuramoto quantum -n 8 -K 2.0 -t 150 --topology ring --scheme shot_sampling --shots 4096 -o data/quantum_ring.npz
```

#### 3. OpenQASM Export (`kuramoto qasm`)
```bash
# Generate OpenQASM 2.0 circuit for 8 oscillators
kuramoto qasm -n 8 -K 1.5 --dt 0.05 -o circuits/scf_step.qasm

# Generate OpenQASM 3.0 circuit with explicit shot measurements
kuramoto qasm -n 16 -K 2.0 --dt 0.02 --version 3.0 --include-measurements -o circuits/scf_qasm3.qasm
```

#### 4. Solver Benchmarks (`kuramoto benchmark`)
```bash
# Compare runtime, steps/sec, and final synchronization strength across all solvers
kuramoto benchmark -n 20 -K 1.5 -t 500 --dt 0.01
```

---

## 🐍 Python API Usage

### 1. Unified Dataset Generation (`kuramoto.api`)
```python
import numpy as np
from kuramoto.api import generate_kuramoto_dataset

# Simulate 20 oscillators using High-Order GA Lie-Group Rotor Integration
dataset = generate_kuramoto_dataset(
    n_oscillators=20,
    coupling=1.5,
    timesteps=1000,
    dt=0.01,
    solver="rkmk4",  # Options: 'rk45', 'rkmk4', 'dopri54', 'midpoint', 'euler_fast', 'quantum'
    topology="small_world",
    symmetry_metrics=True,
    seed=42,
)

theta = dataset["theta"]  # Shape: (1000, 20)
r = dataset["order_parameter"]  # Global synchronization r(t)
print(f"Final order parameter: {r[-1]:.4f}")
```

### 2. Geometric Algebra Rotor Solver (`kuramoto.solvers.RotorSolver`)
```python
from kuramoto.solvers import RotorSolver
import numpy as np

# Instantiate Clifford Cl(2,0) multivector solver
solver = RotorSolver(n_oscillators=50, dim=2, seed=42)
t_eval = np.linspace(0.0, 10.0, 500)

# Simulate using 4th-order Runge-Kutta-Munthe-Kaas (RKMK4) on Spin(2)
times, phases = solver.simulate(K=1.8, t_eval=t_eval, method="rkmk4")

# Check invariants
invariants = solver.compute_lie_invariants(K=1.8)
print(f"Phase shift invariance deviation: {invariants['global_phase_drift']:.2e}")
print(f"Rotor norm deviation: {invariants['max_rotor_norm_error']:.2e}")
```

### 3. Hybrid Quantum SCF Solver (`kuramoto.solvers.QuantumRotorSolver`)
```python
from kuramoto.solvers import QuantumRotorSolver

# Initialize 10-qubit Quantum Self-Consistent Field solver
q_solver = QuantumRotorSolver(
    n_oscillators=10,
    coupling=1.5,
    dt=0.02,
    scheme="expectation",  # 'statevector', 'expectation', or 'shot_sampling'
    seed=42,
)

# Step forward in time
for step in range(100):
    phases, current_r = q_solver.step()

# Export QASM circuit corresponding to current state
qasm_str = q_solver.to_qasm(qasm_version="2.0")
```

---

## 🔬 Mathematical Formulations

### 1. Classical Kuramoto Model
$$\frac{d\theta_i}{dt} = \omega_i + \frac{K}{N} \sum_{j=1}^{N} A_{ij}\sin{(\theta_j - \theta_i)}$$

### 2. Clifford Geometric Algebra $\operatorname{Cl}_{2,0}(\mathbb{R})$ Rotor Evolution
Oscillators are represented as even-grade multivector rotors in the rotor group $\operatorname{Spin}(2)$:
$$R_i(t) = \cos\left(\frac{\theta_i(t)}{2}\right) - \mathbf{e}_{12}\sin\left(\frac{\theta_i(t)}{2}\right) = \exp\left(-\frac{\mathbf{e}_{12}\theta_i(t)}{2}\right)$$
where $\mathbf{e}_{12} = \mathbf{e}_1 \wedge \mathbf{e}_2$ ($\mathbf{e}_{12}^2 = -1$). Rotor dynamics follow the Lie-algebra kinematic equation:
$$\frac{dR_i}{dt} = -\frac{1}{2} \Omega_i(t) R_i(t) \quad \text{where} \quad \Omega_i(t) = \left(\omega_i + \frac{K}{N}\sum_j A_{ij}\sin(\theta_j - \theta_i)\right)\mathbf{e}_{12}$$

### 3. Hybrid Quantum Self-Consistent Field (SCF) Formulation
Each oscillator phase $\theta_j(t)$ is encoded on the equatorial plane of the Bloch sphere:
$$|q_j(t)\rangle = R_Z(\theta_j(t))|+\rangle = \frac{1}{\sqrt{2}}\left(|0\rangle + e^{i\theta_j(t)}|1\rangle\right)$$
Expectation values yield phase coordinates:
$$\langle X_j \rangle = \cos\theta_j, \quad \langle Y_j \rangle = \sin\theta_j \implies \theta_j = \operatorname{atan2}(\langle Y_j \rangle, \langle X_j \rangle)$$
Time evolution applies parallel single-qubit self-consistent field rotations $R_Z(\phi_j^{(t)})$:
$$\phi_j^{(t)} = \left(\omega_j + K \operatorname{Im}\left[e^{-i\theta_j} Z_{\text{local}, j}\right]\right)\Delta t$$

---

## 🎓 Research & Educational Resources

Detailed theoretical derivations, benchmark reports, and interactive Jupyter notebooks are provided in `research/` and `examples/notebooks/`:

- [research/RESEARCH_PREPRINT.md](research/RESEARCH_PREPRINT.md): Formal derivation of GA rotor dynamics and Lie symmetry conservation.
- [research/BENCHMARK_RUNDOWN.md](research/BENCHMARK_RUNDOWN.md): Rigorous numerical comparisons across Classical RK45, GA Rotors (RKMK4, DOPRI54), and Quantum SCF.
- [research/LEARNING_GUIDE.md](research/LEARNING_GUIDE.md): Intuitive guide covering Bivector Torque, Hydrodynamic analogies, and the Quantum Rotor Bridge.
- [research/PRACTICE_PROBLEMS.md](research/PRACTICE_PROBLEMS.md): 10 analytical and computational exercises for geometric synchronization.
- [research/MANUAL_ANALYSIS.md](research/MANUAL_ANALYSIS.md): Code architecture walkthrough and invariant verification notes.
- [examples/notebooks/quantum_sanity_checks.ipynb](examples/notebooks/quantum_sanity_checks.ipynb): Numerical verification of global truncation error, unitary time-reversibility, Bloch equatorial purity, and Central Limit Theorem shot-noise scaling.
- [examples/notebooks/qiskit_hybrid_kuramoto_pipeline.ipynb](examples/notebooks/qiskit_hybrid_kuramoto_pipeline.ipynb): End-to-end Qiskit backend simulation pipeline with OpenQASM export.

---

## 🎨 Visual Identity & Style

The benchmark suite implements the Scriber Core visual identity:
- **Palette Tokens:** High-contrast 4-layer semantic palettes (`SCRIBER_PALETTE`, `PROJECT_COLORS`, `SOLVER_COLORS`).
- **Degree-Preserving Coloring:** Oscillator color identities assigned by graph centrality/degree are strictly preserved across time-series, Fourier, and PSD spectral plots.
- **Publication Ready:** Automatic styling via `kuramoto.analysis.viz.set_style()` with dark-mode card themes and consistent grid lines.

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.