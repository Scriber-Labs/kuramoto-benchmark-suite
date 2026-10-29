# 💫 Kuramoto Benchmark Suite

A high-performance research framework for simulating **Kuramoto oscillator dynamics** using Classical ODEs, **Geometric Algebra (Clifford) Rotors**, and **Hybrid Quantum Self-Consistent Field (SCF)** solvers.

This suite is built for researchers and developers exploring synchronization, Lie-group integrators, and quantum-classical hybrid algorithms.

---

## 🚀 Quickstart

Get up and running in seconds:

### Installation
```bash
# Clone the repository
git clone https://github.com/eigenscribe/kuramoto-benchmark-suite.git
cd kuramoto-benchmark-suite

# Install with development dependencies
pip install -e ".[dev]"
# ...or via uv
uv sync --extra dev
```

### Try it out!
```bash
# Generate a starter dataset
kuramoto datasetforbeginners -o data/demo.npz

# Visualize the trajectories
kuramoto time -i data/demo.npz
```

---

## 🧠 AI-Generated Demos & Notebooks

We maintain a dedicated space for interactive exploration and research proof-of-concepts. All demos, including AI-generated Jupyter notebooks, are stored in:

👉 [**`examples/ai_generated_notebooks/`**](examples/ai_generated_notebooks/)

### Highlighted Notebooks:
- `sanity_checks.ipynb`: Validates GA rotor invariants and energy conservation.
- `qiskit_hybrid_kuramoto_pipeline.ipynb`: End-to-end quantum simulation with Qiskit.
- `quantum_sanity_checks.ipynb`: Unitary reversibility and shot-noise scaling.

---

## 🛠️ Tools & Usage

The suite provides a powerful CLI and a clean Python API.

### Command Line Interface (CLI)
A unified entry point for all operations. For a detailed guide, see:
📖 [**CLI Usage Guide**](docs/CLI_USAGE.md)

**Quick CLI Examples:**
```bash
# GA Rotor simulation (RKMK4)
kuramoto generate -n 50 -K 2.0 --solver rkmk4 -o data/rotor.npz

# Quantum SCF simulation
kuramoto quantum -n 12 -K 1.5 --scheme expectation
```

### Python API
```python
from kuramoto.api import generate_kuramoto_dataset

dataset = generate_kuramoto_dataset(
    n_oscillators=20,
    coupling=1.5,
    solver="rkmk4",
    topology="small_world"
)
```

---

## 🔬 Core Technologies

- **Clifford Geometric Algebra ($\operatorname{Cl}_{2,0}(\mathbb{R})$):** Even-subalgebra multivector rotors for coordinate-free phase evolution.
- **Quantum SCF:** Mapping oscillator states to qubits on the Bloch sphere equatorial plane.
- **Lie-Group Integrators:** High-order `rkmk4` and adaptive `dopri54` solvers for robust manifold-preserving dynamics.

---

## 📖 Further Reading

- [research/RESEARCH_PREPRINT.md](research/RESEARCH_PREPRINT.md): Formal derivation of GA rotor dynamics.
- [research/LEARNING_GUIDE.md](research/LEARNING_GUIDE.md): Intuitive guide to bivector torque and quantum bridges.
- [docs/architecture.md](docs/architecture.md): Deep dive into the codebase structure.

---

## 🎨 Visual Identity
Styled with the **Scriber Core** visual system, featuring publication-ready, degree-preserving palettes and dark-mode aesthetics.

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.