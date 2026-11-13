# 🧪 Scriber Labs: Kuramoto Benchmark Suite

Welcome to the **Scriber Labs** research environment for **Kuramoto Oscillator Dynamics**. This suite is dedicated to exploring mesoscale ensembles, geometric invariance, and the bridge between classical synchronization and quantum coherence.

We specialize in **ZBW (Zitterbewegung) Ensembles**—mesoscopic systems driven by irrational frequency distributions and external vector torques, aiming to map the boundaries of Critical Flicker Fusion (CFF).

---

## 🚀 Research Quickstart

Jump into the simulation environment:

### 🛠️ Installation
```bash
# Clone the repository
git clone https://github.com/eigenscribe/kuramoto-benchmark-suite.git
cd kuramoto-benchmark-suite

# Sync environment using uv (recommended)
uv sync --extra dev
# ...or create and activate a virtual environment, then use pip
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

With `uv`, prefix commands below with `uv run` if the environment is not
activated (for example, `uv run kuramoto --help`).

### 🧠 Interactive Research & AI-Generated Demos
We maintain a living laboratory of interactive experiments, verification notebooks, and proof-of-concepts located in:

👉 [**`notebooks/ai_generated/`**](notebooks/ai_generated/) & [**`notebooks/verification-infrastructure/`**](notebooks/verification-infrastructure/)

**Key Experiments:**
- `zbw_mesoscale_ensemble.ipynb`: Golden-ratio frequency grids, coprime adjacency lattices, and CFF driving.
- `sanity_checks.ipynb`: 12 automated checks validating $\operatorname{Cl}_{2,0}(\mathbb{R})$ rotor invariants, energy conservation, and time-reversibility.
- `failure_modes.ipynb`: Stability boundaries, Nyquist under-resolution, and step-size controller limits.
- `qiskit_hybrid_kuramoto_pipeline.ipynb`: Mapping oscillator phases to Bloch sphere rotations with $\mathcal{O}(1)$ circuit depth.
- `styling_and_visuals_demo.ipynb`: Scriber Core 4-layer design token visualization showcase.

---

## 📟 CLI & Usage Notes

The `kuramoto` CLI is your unified gateway to the simulation engine.

### Quick Commands
```bash
# 1. Generate beginner starter dataset
kuramoto datasetforbeginners -o data/demo.npz

# 2. Run high-order Geometric Algebra Rotor simulation (RKMK4 with symmetry tracking)
kuramoto generate --config data/benchmark/config.json --solver rkmk4 --track-symmetries -o data/rotor.npz

# 3. Execute Quantum SCF simulation on Bloch sphere
kuramoto quantum -n 10 -k 1.5 -t 200 --scheme expectation --plot

# 4. Run ZBW mesoscale simulation with golden-ratio frequency grid and LED driving
kuramoto zbw -n 20 -t 500 -k 1.5 --external-drive -o data/zbw.npz --plot

# 5. Export telemetry with mean field phase and frequency locking for Dash App
kuramoto dash-export -n 50 -k 1.5 -t 200 --topology small_world -o data/dash_export.json

# 6. Visualize phase trajectories & network topology
kuramoto time data/rotor.npz
kuramoto network data/rotor.npz
```

For complete documentation across all 14 subcommands, flags, quantum schemes, and spectral analysis tools:
📖 [**Comprehensive CLI User Guide**](docs/user-guide/CLI_USER_GUIDE.md) | [**Research CLI Notes**](docs/ai-generated-research-notebook/CLI_USAGE.md)

---

## 🔬 Core Methodology

- **The phi-Shield:** Leveraging the Golden Ratio $\phi$ for irrational frequency distributions to avoid resonant lock-in.
- **Geometric Algebra ($\operatorname{Cl}_{2,0}(\mathbb{R})$):** Coordinate-free phase evolution using even-subalgebra multivector rotors.
- **Sparse Coprime Adjacency:** Network topologies driven by number-theoretic coupling constraints.
- **Quantum SCF Bridge:** Self-Consistent Field mapping of Kuramoto dynamics onto quantum expectation values.

---

## 🎨 Visual Identity
All visualizations are powered by the **Scriber Core** UI system, ensuring publication-ready aesthetics with deep-mode support and degree-preserving color palettes.

---

## 📄 License
MIT License. © 2026 Scriber Labs.
