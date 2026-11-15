# 🧪 Scriber Labs: Kuramoto Benchmark Suite

Welcome to the **Scriber Labs** research environment for **Kuramoto Oscillator Dynamics**. This suite is a benchmark-grade synthetic dataset generator, simulation engine, and analytical framework dedicated to exploring mesoscale oscillator ensembles, coordinate-free geometric invariance, and the bridge between classical synchronization and quantum coherence.

We specialize in **ZBW (Zitterbewegung) Ensembles**—mesoscopic systems driven by irrational frequency distributions, sparse coprime network lattices, and external vector torques—as well as Geometric Algebra ($\operatorname{Cl}_{2,0}(\mathbb{R}) / \operatorname{Cl}_{3,0}(\mathbb{R})$) multivector rotor solvers and hybrid Quantum Self-Consistent Field (SCF) models.

---

## 🌟 Key Features & Core Methodology

- **Coordinate-Free Geometric Algebra ($\operatorname{Cl}_{2,0}(\mathbb{R}) / \operatorname{Cl}_{3,0}(\mathbb{R})$):** Multivector rotor evolution on circles $S^1$ and spheres $S^2$, vectorized bivector torques, midpoint, embedded predictor-corrector, Lie-group RKMK4, and adaptive DOPRI 5(4) solvers with exact $U(1)$ phase shift invariance and Hamiltonian energy drift tracking.
- **Classical Adaptive ODE Solvers:** High-precision Scipy Dormand-Prince (RK45) adaptive integrators for reference ground-truth simulation.
- **Quantum SCF Bridge:** Self-Consistent Field mapping of Kuramoto dynamics onto quantum statevectors, expectation values, and shot sampling with $\mathcal{O}(1)$ circuit depth and automated OpenQASM 2.0/3.0 circuit generation.
- **The $\phi$-Shield & ZBW Mesoscale Ensembles:** Leveraging the Golden Ratio $\phi$ for irrational frequency grids and sparse coprime adjacency coupling to eliminate spurious phase-locking.
- **Sub-Nyquist Coprime Time-Domain Sampling:** Dual-rate decimation ($M, N$ strides, $\gcd(M,N)=1$), Extended Euclidean Bézout identity resolution, and Chinese Remainder Theorem (CRT) frequency reconstruction.
- **Complex Topologies:** Unified network generator supporting Ring, Small-World (Watts-Strogatz), Tree of Life, Bipartite, Erdős–Rényi, and Complete graphs.
- **Spectral Analytics & Diagnostics:** Fast Fourier Transform (FFT) amplitude convergence/variability, Power Spectral Density (PSD) diagnostics, and macroscopic order parameter computation $r(t) = \lvert\frac{1}{N}\sum_j e^{i\theta_j}\rvert$.
- **Dash Telemetry Pipeline:** High-speed JSON serialization computing sliding-window frequency locking fraction and mean-field phase $\psi(t) = \operatorname{arg}(\frac{1}{N}\sum_j e^{i\theta_j})$.
- **Visual Identity:** Powered by the **Scriber Core** 4-layer design token styling palette (`cli_info`, `cli_network`, `cli_quantum`, `cli_rotor`, `cli_success`, `cli_warning`, `cli_error`) for publication-ready plots.

---

## 📋 Requirements & Tech Stack

- **Language:** Python `>=3.10` (tested with Python 3.10, 3.11, and 3.12)
- **Package Layout:** `src/` layout (`src/kuramoto/`)
- **Package Manager:** `uv` (recommended) or standard `pip` / `venv`
- **Core Dependencies:**
  - Simulation & Math: `numpy>=1.23`, `scipy>=1.10`, `sympy>=1.12`
  - Geometric Algebra: `clifford>=1.5.1`
  - Graph Theory & Networks: `networkx>=3.0`
  - Visualization: `matplotlib>=3.5`, `seaborn>=0.12`
  - CLI & Formatting: `click>=8.0`, `tabulate>=0.9`
- **Development & QA Extras (`[dev]`):**
  - Testing: `pytest>=7.0`
  - Formatting & Linting: `black>=23.0`, `ruff>=0.1.0`
  - Jupyter Notebooks: `ipykernel>=6.0`

---

## 🛠️ Setup and Installation

### Option A: Using `uv` (Recommended)

```bash
# Clone the repository
git clone https://github.com/eigenscribe/kuramoto-benchmark-suite.git
cd kuramoto-benchmark-suite

# Sync all dependencies including development tools
uv sync --extra dev

# Run CLI or tests directly via uv
uv run kuramoto --help
uv run pytest
```

### Option B: Using Standard Python `venv` & `pip`

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with development dependencies
python -m pip install --upgrade pip
pip install -e ".[dev]"

# Verify CLI installation
kuramoto --help
```

---

## 📟 Entry Points & Usage

The package installs a unified CLI entry point named `kuramoto` (`kuramoto.cli.main:main`). You can also import functional and object-oriented interfaces directly in Python.

### 1. CLI Commands Overview

```bash
# 1. Generate a quick starter dataset for beginners
kuramoto datasetforbeginners -o data/demo.npz

# 2. Run simulation from a JSON config file with RKMK4 rotor solver & symmetry tracking
kuramoto generate --config data/benchmark/config.json --solver rkmk4 --track-symmetries -o data/rotor.npz

# 3. Run Quantum SCF simulation on the Bloch sphere with expectation scheme
kuramoto quantum -n 10 -k 1.5 -t 200 --scheme expectation --plot

# 4. Synthesize and export OpenQASM 2.0 quantum circuits
kuramoto qasm -n 6 -k 1.2 --dt 0.01 -o data/circuit.qasm

# 5. Run ZBW golden-ratio mesoscale simulation with external LED driving
kuramoto zbw -n 20 -t 500 -k 1.5 --external-drive -o data/zbw.npz --plot

# 6. Export telemetry (mean-field phase & locking fraction) for Dash web apps
kuramoto dash-export -n 50 -k 1.5 -t 200 --topology small_world -o data/dash_export.json

# 7. Benchmark and compare Classical ODE, GA Rotor, and Euler solvers
kuramoto benchmark --config data/benchmark/sweep_config.json

# 8. Visualize temporal phase trajectories and time averages
kuramoto time data/rotor.npz

# 9. Visualize oscillator network topology and graph structure
kuramoto network data/rotor.npz

# 10. Visualize natural frequency and phase angle distributions
kuramoto distributions data/rotor.npz

# 11. Plot Fourier amplitude variability diagnostic
kuramoto fouriervariability data/rotor.npz

# 12. Plot discrete Fourier transform convergence
kuramoto fourierconvergence data/rotor.npz

# 13. Plot Power Spectral Density (PSD) variability
kuramoto psdvariability data/rotor.npz

# 14. Plot PSD convergence diagnostic results
kuramoto psdconvergence data/rotor.npz
```

For extended flag options and usage notes, see:
- 📖 [**Comprehensive CLI User Guide**](docs/user-guide/CLI_USER_GUIDE.md)
- 📖 [**Research CLI Notes**](docs/ai-generated-research-notebook/CLI_USAGE.md)

---

### 2. Python Functional API Quickstart

```python
import numpy as np
from kuramoto.api import generate_kuramoto_dataset
from kuramoto.order_parameter import compute_order_parameter, track_lie_symmetries
from kuramoto.solvers.rotor import RotorSolver
from kuramoto.solvers.quantum_rotor import QuantumRotorSolver
from kuramoto.solvers.coprime import CoprimeSamplerWrapper, coprime_reconstruct_frequency
from kuramoto.topologies import load_topology

# Generate synthetic dataset with small-world topology and GA rotor solver
adj = load_topology("small_world", n=12, k=2, p=0.1)
dataset = generate_kuramoto_dataset(
    n_oscillators=12,
    natural_frequencies=np.linspace(-1.0, 1.0, 12),
    coupling=1.8,
    timesteps=100,
    dt=0.01,
    adjacency=adj,
    solver="rotor",
    seed=42,
)

# Compute global order parameter r(t)
r = compute_order_parameter(dataset["theta"])
print(f"Mean Order Parameter: {np.mean(r):.4f}")

# Track U(1) Lie symmetries and energy drift
states = {f"node_{i}": dataset["theta"][:, i] for i in range(12)}
metrics = track_lie_symmetries(states, dataset["time"])
print(f"U(1) Phase Invariance Preserved: {metrics.global_phase_invariant}")
```

---

## 📜 Repository Scripts

The `scripts/` directory contains standalone verification, benchmarking, and export utilities:

| Script | Command | Description |
| :--- | :--- | :--- |
| **Scaling Benchmark** | `python scripts/benchmark_scaling.py` | Compares pairwise Standard $\mathcal{O}(N^2)$ vs Vectorized Geometric Algebra $\mathcal{O}(N)$ scaling across $N \in [50, 500]$. |
| **Dash App Data Export** | `python scripts/export_to_dash.py -i data/rotor.npz -o data/dash.json -f json` | Converts `.npz` simulation datasets to structured JSON or CSV with precomputed macroscopic order parameters. |
| **Rigorous Benchmarks Sweep** | `python scripts/rigorous_benchmarks.py` | Performs full parameter sweeps comparing Vectorized GA vs RK45 ground truth, saving metrics to `data/benchmark/rigorous_results.json` and figures to `plots/benchmarks/`. |
| **GA Rotor Metrics Validation** | `python scripts/validate_ga_rotor_metrics.py` | Validates Hamiltonian energy conservation, phase-space volume contraction $\lambda(t)$, $U(1)$ gauge invariance, and spectral PSD. |
| **3D Spherical Sync Demo** | `python scripts/viz_3d_sync.py` | Simulates multivector rotor dynamics on the 2-sphere $S^2$ and renders initial vs synchronized states to `plots/3d_sync_demo.png`. |

---

## ⚙️ Environment Variables

The suite respects standard terminal and styling environment variables:

| Variable | Values / Example | Description |
| :--- | :--- | :--- |
| `NO_COLOR` | `1`, `true` | When set or non-empty, suppresses all ANSI color output in CLI banners, rules, and semantic messages. |
| `TERM` | `dumb`, `xterm-256color` | When set to `dumb`, ANSI color is disabled. When containing `256color` or `xterm`, rich 256-color palette styling is activated. |
| `COLORTERM` | `truecolor`, `24bit` | When set, enables 24-bit / truecolor terminal rendering support. |

---

## 🧠 Interactive Research & AI-Generated Demos

A living laboratory of interactive research notebooks, verification suites, and failure-mode diagnostics is maintained in:

👉 [**`notebooks/ai_generated/`**](notebooks/ai_generated/) & [**`notebooks/verification-infrastructure/`**](notebooks/verification-infrastructure/)

**Key Notebooks:**
- [`zbw_mesoscale_ensemble.ipynb`](notebooks/ai_generated/zbw_mesoscale_ensemble.ipynb): Golden-ratio frequency grids, coprime adjacency lattices, and Critical Flicker Fusion (CFF) macroscopic driving.
- [`sanity_checks.ipynb`](notebooks/verification-infrastructure/sanity_checks.ipynb): Automated checks validating $\operatorname{Cl}_{2,0}(\mathbb{R})$ rotor invariants, energy conservation, and time-reversibility.
- [`failure_modes.ipynb`](notebooks/verification-infrastructure/failure_modes.ipynb): Stability boundaries, Nyquist under-resolution, and step-size controller limits.
- [`qiskit_hybrid_kuramoto_pipeline.ipynb`](notebooks/ai_generated/qiskit_hybrid_kuramoto_pipeline.ipynb): Mapping oscillator phases to Bloch sphere rotations with $\mathcal{O}(1)$ circuit depth.
- [`styling_and_visuals_demo.ipynb`](notebooks/ai_generated/styling_and_visuals_demo.ipynb): Scriber Core 4-layer design token visualization showcase.

---

## 🧪 Testing & Quality Assurance

### Running Tests

```bash
# Run all unit and integration tests (quiet mode by default)
uv run pytest

# Run with verbose test-by-test output
uv run pytest -v

# Run a specific test suite
uv run pytest tests/test_ga_rotor_invariants.py
uv run pytest tests/test_quantum_rotor_solver.py

# Run tests matching a keyword filter
uv run pytest -k "coprime or rotor or zbw"
```

### Code Style & Linting

```bash
# Format codebase with Black (88 character line limit, py310 target)
uv run black .

# Lint codebase with Ruff (E, W, F, I, B, C4 rule sets)
uv run ruff check .

# Apply automatic Ruff fixes
uv run ruff check --fix .
```

---

## 📂 Project Structure

```text
kuramoto-benchmark-suite/
├── LICENSE                               # MIT License
├── README.md                             # Repository Documentation
├── pyproject.toml                        # Build configuration, deps, Ruff, Black & Pytest settings
├── uv.lock                               # Deterministic dependency lockfile
├── data/                                 # Benchmark configurations, .npz datasets & telemetry
│   ├── benchmark/                        # Benchmarking sweep configs and test datasets
│   └── examples/                         # Starter demo datasets
├── docs/                                 # Research preprints, developer guidelines & user guides
│   ├── ai-generated-research-notebook/   # Preprint drafts, CLI guides & Floquet walkthroughs
│   ├── developer/                        # House rules, boilerplate templates & styling tokens
│   └── user-guide/                       # Comprehensive CLI User Guide
├── notebooks/                            # Interactive Jupyter research environment
│   ├── ai_generated/                     # ZBW ensembles, Qiskit pipelines & sanity checks
│   ├── practice-problems/                # Coding exercises and worked problems
│   └── verification-infrastructure/      # Automated sanity checks and failure mode notebooks
├── plots/                                # Exported publication-ready figures & benchmark plots
│   ├── benchmarks/                       # Accuracy and scaling performance plots
│   └── validation/                       # Hamiltonian energy drift and contraction rate plots
├── scripts/                              # Standalone utility, benchmark & export scripts
│   ├── benchmark_scaling.py              # Pairwise vs Vectorized GA scaling benchmark
│   ├── export_to_dash.py                 # Telemetry exporter for Kuramoto Dash App
│   ├── rigorous_benchmarks.py            # Rigorous RK45 vs GA Rotor benchmark sweep
│   ├── validate_ga_rotor_metrics.py      # Rotor invariant & Hamiltonian drift validator
│   └── viz_3d_sync.py                    # 3D spherical synchronization visualizer
├── src/                                  # Source root (src/ layout)
│   └── kuramoto/                         # Core Python package
│       ├── __init__.py                   # Package exports
│       ├── api.py                        # Public generate_kuramoto_dataset API
│       ├── config.py                     # Canonical configuration dataclass
│       ├── dash_export.py                # Telemetry pipeline for Dash integration
│       ├── dataset.py                    # KuramotoDataset container (.npz / .h5 export)
│       ├── model.py                      # KuramotoModel core orchestration engine
│       ├── order_parameter.py            # Order parameter r(t) & Lie symmetry tracking
│       ├── solver_types.py               # Canonical solver aliases and options
│       ├── topologies/                   # Graph generators (Ring, Small-World, Tree of Life, etc.)
│       ├── analysis/                     # Spectral decomposition, FFT, PSD & viz engine
│       ├── cli/                          # Click CLI commands, banners & styling palette
│       ├── metrics/                      # Analytical engine & diagnostic metrics
│       ├── models/                       # Specialized model generators (e.g. ZBW generator)
│       ├── quantum/                      # OpenQASM circuit generation engine
│       ├── solvers/                      # Classical (RK45), GA Rotor & Quantum SCF solvers
│       └── utils/                        # Phase unwrapping and reproducible RNG utilities
└── tests/                                # Test suite (88 test cases)
    ├── test_analytics_engine.py
    ├── test_cli_style.py
    ├── test_coprime_sampler.py
    ├── test_dash_export.py
    ├── test_ga_rotor_invariants.py
    ├── test_generate_kuramoto_dataset.py
    ├── test_quantum_rotor_solver.py
    ├── test_quasi_periodic_fibonacci.py
    └── test_zbw_generator.py
```

---

## 🗺️ Roadmap & Planned Work

- [x] Vectorized $\operatorname{Cl}_{2,0}(\mathbb{R})$ & $\operatorname{Cl}_{3,0}(\mathbb{R})$ multivector rotor engines with midpoint and Lie-group RKMK4.
- [x] Quantum Self-Consistent Field (SCF) simulation with OpenQASM 2.0/3.0 export.
- [x] Sub-Nyquist dual-rate coprime time-domain sampling and CRT reconstruction.
- [x] ZBW golden-ratio irrational frequency grid generator with external macroscopic LED drive.
- [ ] **TODO:** Real-device hardware integration pipeline with Qiskit Runtime for quantum expectation sampling.
- [ ] **TODO:** Distributed MPI/GPU acceleration for extreme-scale ensembles ($N > 10^5$).
- [ ] **TODO:** Interactive WebAssembly / Pyodide browser-native simulation visualizer.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).  
Copyright © 2025–2026 eigenscribe / Scriber Labs.
