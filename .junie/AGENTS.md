# Kuramoto Benchmark Suite - Developer Guide

This document provides technical guidelines, build/configuration instructions, testing conventions, and architectural details for developers contributing to the `kuramoto-benchmark-suite` codebase.

---

## 0. Agent Guideline Bridge (Scriber Core)

Shared house rules and reusable code templates are maintained in the [`scriber-core`](https://github.com/eigenscribe/scriber-core) submodule, mounted at `.scriber-core/`. Treat the following as canonical references when generating, reviewing, or styling code:

- **Python Rules**: `.scriber-core/house-rules/python-rules.md`
- **CSS / UI System**: `.scriber-core/house-rules/css-rules.md`
- **Python Numeric Template**: `.scriber-core/boilerplates/python/gold-standard-boilerplate.py`
- **Visualization Bootstrap Template**: `.scriber-core/boilerplates/python/visualization_boilerplate.py`

---

## 1. Build and Configuration Instructions

### 1.1 Environment Requirements
- **Python**: `>= 3.10` (tested with Python 3.10, 3.11, and 3.12)
- **Package Layout**: `src/` layout (`src/kuramoto/`)
- **Package Manager**: Compatible with standard `uv`, `pip`, or `venv`

### 1.2 Setup and Installation

#### Option A: Using `uv` (Recommended)
```bash
# Ensure uv is in PATH (e.g. /opt/homebrew/bin or ~/.cargo/bin)
export PATH="/opt/homebrew/bin:~/.cargo/bin:$PATH"

# Sync all dependencies including development tools (pytest, black, ruff, ipykernel)
uv sync --extra dev

# Run tools directly via uv environment
uv run pytest
uv run kuramoto --help
```

#### Option B: Using Standard Python `venv` & `pip`
```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package in editable mode with development dependencies
pip install -e ".[dev]"
```

### 1.3 Core Dependencies & Extras
- **Core Simulation & Analysis**: `numpy>=1.23`, `scipy>=1.10`, `networkx>=3.0`, `seaborn>=0.12`, `matplotlib>=3.5`, `tabulate>=0.9`, `click>=8.0`, `sympy>=1.12`
- **Geometric Algebra**: `clifford>=1.5.1` (used for $\operatorname{Cl}_{2,0}(\mathbb{R})$ / $\operatorname{Cl}_{3,0}(\mathbb{R})$ even-subalgebra rotor solvers)
- **Development & QA**: `pytest>=7.0`, `black>=23.0`, `ruff>=0.1.0`, `ipykernel>=6.0`

### 1.4 CLI Verification
The project installs a CLI entry point named `kuramoto` (`kuramoto.cli.main:main`). Verify installation via:
```bash
uv run kuramoto --help
# or with activated virtualenv:
kuramoto --help
```

---

## 2. Testing Information

### 2.1 Test Configuration
- **Configuration File**: `pyproject.toml` (`[tool.pytest.ini_options]`)
- **Test Discovery Root**: `tests/`
- **Python Path Injection**: `src/` is automatically added to `sys.path` during test discovery (`pythonpath = ["src"]`).
- **Default Options**: `addopts = "-q"`

### 2.2 Executing Tests

```bash
# Run all tests quietly (default)
uv run pytest

# Run with verbose test-by-test output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_generate_kuramoto_dataset.py

# Run a specific test case within a file
uv run pytest tests/test_ga_rotor_invariants.py::test_rotor_u1_invariance

# Run tests matching a keyword filter
uv run pytest -k "quantum or rotor"
```

### 2.3 Guidelines for Adding New Tests
1. **File Location & Naming**: Add new test files inside `tests/` with the filename prefix `test_*.py`.
2. **Function & Class Naming**: Test functions must follow `test_*()`, and test classes should follow `Test*`.
3. **Imports**: Import directly from `kuramoto.<module>` (e.g. `from kuramoto.api import generate_kuramoto_dataset`).
4. **Reproducibility**: Always pass explicit `seed` parameters or use `np.random.default_rng(seed)` when testing stochastic solvers, random graph generators, or frequency initializations.
5. **In-Module Smoke Tests**: In accordance with project conventions, non-trivial modules in `src/kuramoto/` should include a private `_run_smoke_test()` function invoked by `if __name__ == "__main__": main()`.

### 2.4 Verified Test Examples
The following examples demonstrate complete, verified test cases across key subsystems (data generation, GA rotor invariants, quantum SCF, coprime sampling, and Dash telemetry export):

```python
import numpy as np
import pytest

from kuramoto.api import generate_kuramoto_dataset
from kuramoto.order_parameter import compute_order_parameter, track_lie_symmetries
from kuramoto.solvers.rotor import RotorSolver
from kuramoto.solvers.quantum_rotor import QuantumRotorSolver
from kuramoto.solvers.coprime import CoprimeSamplerWrapper, coprime_reconstruct_frequency
from kuramoto.dash_export import compute_mean_field_phase, compute_locking_fraction, export_for_dash
from kuramoto.topologies import load_topology


def test_kuramoto_simulation_and_order_parameter():
    """Verify dataset output shapes and order parameter bounds [0, 1]."""
    n_oscillators = 10
    omega = np.ones(n_oscillators)
    timesteps = 50
    dt = 0.02

    dataset = generate_kuramoto_dataset(
        n_oscillators=n_oscillators,
        natural_frequencies=omega,
        coupling=1.5,
        timesteps=timesteps,
        dt=dt,
        seed=42,
    )

    # Validate output dictionary structure
    assert "theta" in dataset
    assert dataset["theta"].shape == (timesteps, n_oscillators)

    # Validate order parameter computation
    r = compute_order_parameter(dataset["theta"])
    assert r.shape == (timesteps,)
    assert np.all((r >= 0.0) & (r <= 1.0 + 1e-6))


def test_ga_rotor_solver_and_lie_symmetry():
    """Verify Geometric Algebra RotorSolver and U(1) phase shift invariance."""
    n_oscillators = 8
    t_eval = np.linspace(0.0, 1.0, 20)
    solver = RotorSolver(n_oscillators=n_oscillators, seed=42)

    t_out, phases = solver.simulate(K=1.2, t_eval=t_eval, dt_internal=0.01)
    assert phases.shape == (20, n_oscillators)

    states = {f"node_{i}": phases[:, i] for i in range(n_oscillators)}
    metrics = track_lie_symmetries(states, t_out)
    assert metrics.global_phase_invariant is True


def test_quantum_rotor_solver_and_qasm():
    """Verify QuantumRotorSolver statevector evolution and OpenQASM export."""
    n_oscillators = 4
    solver = QuantumRotorSolver(n_oscillators=n_oscillators, seed=42)
    t_eval = np.linspace(0.0, 0.5, 10)

    t_out, phases = solver.simulate(K=1.0, t_eval=t_eval, scheme="statevector")
    assert phases.shape == (10, n_oscillators)

    qasm_str = solver.to_qasm(K=1.0, dt=0.01)
    assert "OPENQASM 2.0;" in qasm_str
    assert "qreg q[4];" in qasm_str


def test_coprime_sampling_and_reconstruction():
    """Verify dual-channel coprime time-domain sampling and CRT reconstruction."""
    M, N = 7, 11
    k_true = 45
    k_m = k_true % M
    k_n = k_true % N
    k_reconstructed = coprime_reconstruct_frequency(k_m=k_m, k_n=k_n, M=M, N=N)
    assert k_reconstructed == k_true

    solver = RotorSolver(n_oscillators=6, seed=42)
    wrapper = CoprimeSamplerWrapper(solver=solver, M=M, N=N, record_phases=True)
    res = wrapper.simulate(K=1.0, dt=0.01, cycles=1)
    assert res.total_steps == M * N
    assert len(res.t_a) == (M * N // N) + 1
    assert len(res.t_b) == (M * N // M) + 1


def test_dash_export_pipeline(tmp_path):
    """Verify Dash export pipeline with locking fraction and mean-field phase."""
    adj = load_topology("small_world", n=10, k=2, p=0.1)
    dataset = generate_kuramoto_dataset(
        n_oscillators=10,
        natural_frequencies=np.ones(10),
        coupling=1.5,
        timesteps=30,
        dt=0.02,
        adjacency=adj,
        seed=42,
    )
    psi = compute_mean_field_phase(dataset["theta"])
    locking = compute_locking_fraction(dataset["theta"], dataset["time"])
    assert psi.shape == (30,)
    assert locking.shape == (30,)

    out_file = str(tmp_path / "dash_data.json")
    export_for_dash(dataset, out_file)
    assert tmp_path.joinpath("dash_data.json").exists()
```

---

## 3. Architecture & Code Style Guidelines

### 3.1 Structural Code Layout ("Gold Standard" Pattern)
Modules follow the structural template defined in `docs/developer/HOUSE_RULES.md` and `docs/developer/python_boilerplate.py`:
- **Narrative Flow**: `"What exists -> what you're allowed to call -> how it works -> proof it works"`
- **Section Dividers (Numbered Emojis)**:
  - `0️⃣` / `🎭` **Definitions, Constants & Types**: Type aliases (`NDArray`, `Final`), protocols, global constants.
  - `1️⃣` **Public API**: Functions and classes intended for external consumers.
  - `2️⃣` / `3️⃣` **Internal Logic & Helpers**: Private functions (`_internal_*` / `_helper_*`) encapsulating algorithms and numerical routines.
  - `💨` **Smoke Tests**: Quick sanity check function `_run_smoke_test()`.
  - `🔥` **Entry Point**: `def main() -> None:` followed by `if __name__ == "__main__": main()`.
- **`if __name__ == "__main__":` Rule**: Reserved **only** for smoke tests, lightweight demonstrations, and sanity checks. Never place long training loops or parameter sweeps directly in `main()`.

### 3.2 Type Annotations & Docstrings
- Include `from __future__ import annotations` at the top of every module.
- Type annotate all public function signatures, parameters, and return types (`NDArray[np.floating]`, `Final[int]`, union syntax `float | NDArray`).
- Use **NumPy-style docstrings** on all public classes, functions, and nontrivial private helpers:
  ```python
  def simulate_step(theta: NDArray, omega: NDArray, dt: float) -> NDArray:
      """
      Perform a single forward simulation step.

      Parameters
      ----------
      theta : NDArray
          Current phase array.
      omega : NDArray
          Natural frequencies.
      dt : float
          Integration time step.

      Returns
      -------
      NDArray
          Updated phase array.
      """
  ```

### 3.3 Formatting, Linting & Hygiene Rules
- **Black**: Max line length `88`, target Python `py310`.
  ```bash
  uv run black .
  ```
- **Ruff**: Configured with rules `E`, `W`, `F`, `I` (isort), `B` (bugbear), `C4` (comprehensions).
  ```bash
  uv run ruff check .
  uv run ruff check --fix .
  ```
- **Explicit `__init__.py` Exports**: Subpackages must define explicit `__all__` lists without wildcard imports.
- **Centralized Constants**: Canonical solver aliases and options reside in `kuramoto.solver_types` to eliminate duplication across CLI, models, and solvers.
- **Modern NumPy RNG**: Prefer `np.random.default_rng(seed)` or `kuramoto.utils.get_rng(seed)` over legacy `np.random.seed()`.

### 3.4 Key Subsystem Architecture

| Subsystem | Module | Description |
| :--- | :--- | :--- |
| **Public Functional API** | `kuramoto.api` | `generate_kuramoto_dataset()` functional entry point unifying model setup, topology resolution, solver execution, and symmetry tracking. |
| **Model Orchestration** | `kuramoto.model` | `KuramotoModel` class managing internal state, natural frequency arrays, adjacency graph injection, noise, and solver dispatching. |
| **Data Serialization** | `kuramoto.dataset` | `KuramotoDataset` container managing immutability, metadata, NumPy `.npz`, and HDF5 `.h5` export. |
| **Classical ODE Solvers** | `kuramoto.solvers.rk45` | Scipy Dormand-Prince adaptive ODE integrators. |
| **Clifford GA Rotor Solvers** | `kuramoto.solvers.rotor` | $\operatorname{Cl}_{2,0}(\mathbb{R})$ and $\operatorname{Cl}_{3,0}(\mathbb{R})$ multivector rotor evolution on $S^1$ / $S^2$, vectorized bivector torques, midpoint, embedded predictor-corrector, Lie-group RKMK4, and adaptive DOPRI 5(4). |
| **Quantum SCF Solvers** | `kuramoto.solvers.quantum_rotor` | Quantum Self-Consistent Field (SCF) $N$-qubit statevector, expectation, and shot-sampling solvers with OpenQASM 2.0/3.0 circuit generation (`kuramoto.quantum.circuit_gen`). |
| **Sub-Nyquist Coprime Sampler** | `kuramoto.solvers.coprime` | Dual-rate time-domain decimation ($M, N$ strides, $\gcd(M,N)=1$), Extended Euclidean Bézout identity resolution, Chinese Remainder Theorem (CRT) frequency index reconstruction, and spectral drift detection. |
| **Observables & Symmetries** | `kuramoto.order_parameter` | Global order parameter $r(t) = \lvert\frac{1}{N}\sum_j e^{i\theta_j}\rvert$, complex order parameter, and Lie symmetry tracking (global $U(1)$ phase shift invariance, Noether energy drift). |
| **Network Topologies** | `kuramoto.topologies` | Topology loader (`load_topology`) generating Ring, Small-World (Watts-Strogatz), Tree of Life, Bipartite, Erdős–Rényi, and Complete graphs. |
| **ZBW Golden-Ratio Ensemble** | `kuramoto.models.zbw_generator` | `ZBWKuramotoDataGenerator` implementing the $\phi$-shield irrational frequency grid, sparse coprime adjacency lattice, and external macroscopic LED driving field. |
| **Dash App Telemetry Export** | `kuramoto.dash_export` | Enriched JSON telemetry pipeline computing mean field phase $\psi(t) = \operatorname{arg}(\frac{1}{N}\sum e^{i\theta_j})$ and sliding-window frequency locking fraction. |
| **Spectral Analytics & Viz** | `kuramoto.analysis` | Spectral decomposition, Fourier amplitude convergence/variability, PSD variability, and publication-ready plotting (`viz.py`). |
| **CLI Suite** | `kuramoto.cli` | Click CLI implementing commands: `generate`, `datasetforbeginners`, `time`, `network`, `distributions`, `fouriervariability`, `fourierconvergence`, `psdvariability`, `psdconvergence`, `quantum`, `qasm`, `benchmark`. |
| **CLI Semantic Styling** | `kuramoto.cli.style` | Scriber Core 4-layer design token styling palette (`cli_info`, `cli_network`, `cli_quantum`, `cli_rotor`, `cli_success`, `cli_warning`, `cli_error`). |
