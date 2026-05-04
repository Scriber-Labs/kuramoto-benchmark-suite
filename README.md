# 🎭 Kuramoto Benchmark Suite

A research-grade synthetic dataset generator and diagnostic suite for coupled oscillator systems.

This repository provides a modular, CLI-driven framework for simulating Kuramoto dynamics and performing spectral/topological analysis. Inspired by the `satis` CFD tool and designed with a "What -> Who -> How -> Proof" flow.

---

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/your-username/kuramoto-benchmark-suite.git
cd kuramoto-benchmark-suite
pip install .
```

### Beginner's Workflow
Generate a demo dataset and start your first diagnostic:
```bash
# 1. Generate demo dataset
kuramoto datasetforbeginners

# 2. Visualize the network structure
kuramoto network data/examples/demo_dataset.npz --gradient gradient_4

# 3. Check the temporal signal and order parameter
kuramoto time data/examples/demo_dataset.npz -t 5.0

# 4. Perform Fourier analysis
kuramoto fouriervariability data/examples/demo_dataset.npz -f 0.16
```

---

## 🛠️ Command Line Interface (CLI)

The `kuramoto` command provides a full suite of diagnostics:

| Command | Description |
| :--- | :--- |
| `datasetforbeginners` | Copy/generate a demo dataset to start using the suite. |
| `generate` | Generate a dataset from a JSON configuration file. |
| `network` | Visualize the oscillator network (colored by degree). |
| `distributions` | Plot histograms of natural frequencies and initial phases. |
| `time` | Plot phase trajectories (consistent coloring) and $r(t)$. |
| `fouriervariability` | Check Fourier coefficients (consistent coloring) at a target frequency. |
| `fourierconvergence` | Plot convergence of Fourier amplitude over increasing signal length. |
| `psdvariability` | Analyze Power Spectral Density (PSD) and energy distribution. |
| `psdconvergence` | Compare PSD estimates across different time segments. |

---

## 🧪 Advanced Topological Analysis

The suite includes specialized tools for analyzing the underlying graph structures:

```python
from kuramoto.topologies import load_topology, compute_chromatic_polynomial

# Load a canonical topology
G = load_topology("tree_of_life", return_graph=True)

# Compute the chromatic polynomial
poly = compute_chromatic_polynomial(G)
print(f"Chromatic Polynomial: {poly}")
```

Supported topologies: `ring`, `complete`, `small_world`, `random`, and the canonical `tree_of_life` (10 nodes, 22 edges).

### Simulation via JSON
Generate complex benchmarks using JSON configurations:
```bash
kuramoto generate --config my_config.json --output data/benchmark_1.npz
```

Example `my_config.json`:
```json
{
    "n_oscillators": 25,
    "coupling_strength": 1.2,
    "topology": "small_world",
    "timesteps": 1000,
    "dt": 0.05,
    "seed": 42,
    "frequency_distribution": {
        "type": "normal",
        "mean": 0.0,
        "std": 1.0
    }
}
```

---

## 🎨 Visual Identity & Style

The project uses a standard 'house style' for all code and visualizations:
- **Gradient Themes**: 8 custom gradients (`gradient_0` to `gradient_7`) for consistent data coloring.
- **Consistent Coloring**: Oscillators are colored by their degree in the network plot, and this coloring is preserved across time-series and spectral diagnostics.
- **Seaborn Integration**: Publication-ready plots with high-density markers.
- **House Rules**: Code follows strict emoji-numbered sectioning and NumPy-style documentation (see `templates/HOUSE_RULES.md`).

---

## 🧬 Mathematical Model

The evolution of $N$ phase oscillators is governed by:

$$\frac{d\theta_i}{dt} = \omega_i + \frac{K}{N} \sum_{j=1}^{N} A_{ij} \sin(\theta_j - \theta_i)$$

where $A_{ij}$ is the adjacency matrix and $K$ is the coupling strength.

---

## 🏅 Rule of Thumb

If someone scrolls a file top-to-bottom, the conceptual story should flow:

> [!summary] **What exists** -> **What you're allowed to call** -> **How it works** -> **Proof it works**

---

## 📄 License
MIT License. See `LICENSE` for details.
