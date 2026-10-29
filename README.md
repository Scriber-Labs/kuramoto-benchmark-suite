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
# ...or via standard pip
pip install -e ".[dev]"
```

### 🧠 AI-Generated Demos & Research Notebooks
We maintain a living laboratory of interactive experiments. All proof-of-concepts, including AI-generated Jupyter notebooks, are stored in:

👉 [**`examples/ai_generated_notebooks/`**](examples/ai_generated_notebooks/)

**Key Experiments:**
- `zbw_mesoscale_ensemble.ipynb`: **[NEW]** Golden-ratio frequency grids and coprime adjacency networks.
- `sanity_checks.ipynb`: Validating $\operatorname{Cl}_{2,0}(\mathbb{R})$ rotor invariants and energy conservation.
- `qiskit_hybrid_kuramoto_pipeline.ipynb`: Mapping oscillator phases to Bloch sphere rotations.

---

## 📟 CLI & Usage Notes

The `kuramoto` CLI is your gateway to the simulation engine.

### Quick Commands
```bash
# Generate a mesoscale dataset (RK45)
kuramoto generate -n 100 -K 0.8 --solver rk45 -o data/mesoscale.npz

# Run a Geometric Algebra Rotor simulation (RKMK4)
kuramoto generate -n 50 -K 2.0 --solver rkmk4 -o data/rotor.npz

# Visualize phase trajectories
kuramoto time -i data/mesoscale.npz
```

For full documentation of flags and advanced usage, see:
📖 [**CLI Usage Guide**](docs/CLI_USAGE.md)

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