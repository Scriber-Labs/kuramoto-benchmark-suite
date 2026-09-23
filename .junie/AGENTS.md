# Kuramoto Benchmark Suite - Developer Guide

This document provides technical guidelines, build/configuration instructions, testing conventions, and architectural details for developers contributing to the `kuramoto-benchmark-suite` codebase.

---

## 1. Build and Configuration Instructions

### 1.1 Environment Requirements
- **Python**: `>= 3.10`
- **Package Layout**: `src/` layout (`src/kuramoto/`)
- **Package Manager**: Compatible with standard `pip`, `venv`, or `uv`

### 1.2 Setup and Installation

#### Option A: Using `uv` (Recommended)
```bash
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
- **Geometric Algebra**: `clifford>=1.5.1` (used for $\operatorname{Cl}_{2,0}(\mathbb{R})$ even-subalgebra rotor solvers)
- **Development & QA**: `pytest>=7.0`, `black>=23.0`, `ruff>=0.1.0`, `ipykernel>=6.0`

### 1.4 CLI Verification
The project installs a CLI entry point named `kuramoto` (`kuramoto.cli.main:main`). Verify installation via:
```bash
kuramoto --help
# or via uv:
uv run kuramoto --help
```

---

## 2. Testing Information

### 2.1 Test Configuration
- **Configuration File**: `pyproject.toml` (`[tool.pytest.ini_options]`)
- **Test Discovery Root**: `tests/`
- **Python Path Injection**: `src/` is automatically added to `sys.path` during test discovery (`pythonpath = ["src"]`).

### 2.2 Executing Tests

```bash
# Run all tests quietly (default addopts = "-q")
pytest
# or via uv:
uv run pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_generate_kuramoto_dataset.py

# Run a specific test case
pytest tests/test_generate_kuramoto_dataset.py::test_determinsim

# Run tests with keyword filter
pytest -k "determinsim or shapes"
```

### 2.3 Guidelines for Adding New Tests
1. **File Location & Naming**: Add tests inside `tests/` with the filename prefix `test_*.py`.
2. **Function Naming**: Test functions must follow the `test_*()` pattern.
3. **Imports**: Import directly from `kuramoto.<module>` (e.g. `from kuramoto.api import generate_kuramoto_dataset`).
4. **Reproducibility**: Always pass explicit `seed` parameters when testing stochastic solvers or random frequency initializations.
5. **In-Module Smoke Tests**: In accordance with project conventions, non-trivial modules in `src/kuramoto/` should include a private `_run_smoke_test()` function invoked by `if __name__ == "__main__": main()`.

### 2.4 Verified Test Example
The following is an example demonstrating a complete test case verifying dataset generation and order parameter bounded dynamics:

```python
import numpy as np
from kuramoto.api import generate_kuramoto_dataset
from kuramoto.order_parameter import compute_order_parameter


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
```

---

## 3. Architecture & Code Style Guidelines

### 3.1 Structural Code Layout ("Gold Standard" Pattern)
Modules follow the structure outlined in `templates/HOUSE_RULES.md` and `templates/python_boilerplate.py`:
- **Narrative Flow**: `"What exists -> what you're allowed to call -> how it works -> proof it works"`
- **Section Dividers (Numbered Emojis)**:
  - `0️⃣` / `🎭` **Definitions, Constants & Types**: Type aliases (`NDArray`, `Final`), protocols, global constants.
  - `1️⃣` **Public API**: Functions and classes intended for external consumers.
  - `2️⃣` / `3️⃣` **Internal Logic & Helpers**: Private functions (`_internal_*`) encapsulating algorithms and validation.
  - `💨` **Smoke Tests**: Quick sanity check `_run_smoke_test()`.
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

### 3.3 Formatting and Linting
The project enforces Black and Ruff standards defined in `pyproject.toml`:
- **Black**: Max line length `88`, target Python `py310`.
  ```bash
  black .
  ```
- **Ruff**: Configured with rules `E`, `W`, `F`, `I` (isort), `B` (bugbear), `C4` (comprehensions).
  ```bash
  ruff check .
  ruff check --fix .
  ```

### 3.4 Key Subsystem Architecture
- **`kuramoto.api`**: Stable functional interface (`generate_kuramoto_dataset`) abstracting internal model details.
- **`kuramoto.model`**: `KuramotoModel` class orchestrating state arrays, initial conditions, network topology, and numerical integration.
- **`kuramoto.dataset`**: `KuramotoDataset` container managing data serialization (`.npz`, `.h5`) and metadata.
- **`kuramoto.solvers`**: Numerical integrators including Scipy ODE wrappers, stochastic Euler-Maruyama (`euler_maruyama`), and Geometric Algebra rotor evolution (`rotor`).
- **`kuramoto.order_parameter`**: Global order parameter $r(t) = |\frac{1}{N}\sum_j e^{i\theta_j}|$ and Lie symmetry tracking ($U(1)$ phase invariance diagnostics).
- **`kuramoto.topologies`**: Graph generators (ring, small-world, tree-of-life, bipartite, Erdos-Renyi, complete) loaded via `kuramoto.topologies.load_topology()`.
- **`kuramoto.analysis`**: Spectral diagnostics, Fourier amplitude convergence, PSD variability, and visualization plotting utilities (`viz.py`).
- **`kuramoto.cli`**: Click-powered command suite implementing `kuramoto` subcommands (`generate`, `network`, `distributions`, `time`, `fourieravailability`, `psdvariability`, etc.).
