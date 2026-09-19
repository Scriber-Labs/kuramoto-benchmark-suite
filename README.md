# 💫 Kuramoto Benchmark Suite

A research-grade synthetic dataset generator and diagnostic suite for coupled oscillator systems.

This repository provides a modular, CLI-driven framework for simulating Kuramoto dynamics and performing 
spectral/topological analysis. Inspired by the `satis` CFD tool and designed with a "What -> Who -> How -> Proof" flow.

**New in v0.3 j(Sep 2026)**
- ⚛️  **Geometric Algebra Rotor Solve:** $\operatorname{Cl}_{2,0}(\mathbb{R})$ even-subalgebra implementation for phase 
    evolution.
- 🔗 **Lie Symmetry Analysis:** $\operatorname{U}(1)$ phase invariance and NOether charge diagnostics.
- 📊 **Enhanced Spectral Analysis:** Synchronization transition detection and harmonic cascade analysis.
- 🛠️️ **Extended CLI Properties:** Solver section and symmetry tracking flags

---

## 🚀 Quickstart

### Installation
```bash
git clone https://github.com/yourusername/kuramoto-benchmark-suite.git
cd kuramoto-benchmark-suite
pip install .
```

### Optional Dependencies (for Geometric Algebra features)
```bash
pip install clifford>=1.6.0
```

### 🔰 Beginner's Guide
Generate a demo dataset and start your first diagnostic:
```bash
# 1. Generate datasetforbeginners
kuramoto datasetforbeginners

# 2. Visualize the network structure
kuramoto network data/examples/demo_dataset.npz --gradient gradient_4

# 3. Check the temporal signal and order parameter
kuramoto time data/examples/demo_dataset.npz -t 5.0

# 4. Perform Fourier analysis
kuramoto fourieravailability data/examples/demo_dataset.npz -f 0.16
```

---

## 🛠️ Command Line Interface (CLI)
The `kuramoto` command provides a full suite of diagnostics.

| **Command** | **Description** |
|:------------|:----------------|
| `datasetforbeginners` | Copy/generate a demo dataset to start using the suite. |
| `generate` | Generate a dataset from a JSON configuration file *(with solver options)* |
| `network` | Visualize the oscillator network (colored by degree) |
| `distributions` | Plot histograms of natural frequencies and initial phases |
| `time` | Plot phase trajectories (consistent coloring) and $r(t)$ |
| `fourieravailability` | Check Fourier coefficients (consistent coloring) at a target frequency |
| `fourierconvergence` | Plot convergence of Fourier amplitude over increasing signal legnth |
| `psdvariability` | Analyze Power Spectral Density (PSD) and energy distribution |
| `psdconvergence` | Compare PSD estimates across different time segments |

### New CLI Options (v0.3+)
```bash
# Generate dataset with GA rotor solver and symmetry tracking
kuramoto generate --config my_config.json -o data/rotor.npz \
    --solver rotor --track-symmetries
    
# Available solver choices
kuramoto generate --solver euler      # Standard Euler integration
kuramoto generate --solver rk45       # SciPy adaptive RK45
kuramoto generate --solver rotor      # Geometric Algebra Cl(2) rotors

# Lie symmetry tracking (requires --solver rotor)
kuramoto generate --track-symmetries  # Enables U(1) invariance diagnostics
```

#### ⚗️ Advanced Analysis Features

The new `RotorSolver` implements Kuramoto dynamics using Clifford algebra ($\operatorname{Cl}(2)$):
```bash
from kuramoto.solvers import RotorSolver

# Initialize GA-based solver
solver = RotorSolver(n_oscillators=100, dim=2, seed=27)

# Run simulation
times, phases = solver.simulate(K=1.5, t_eval=times)

W Extract synchronization strength
sync = solver.get_synchronization_strength()
```

#### Key Concepts
- Oscillators encoded as **rotors** in even subalgebra: $$R=e^{-\frac{B\theta}{2}}$$
- Rotation plane bivector: $$B=\mathbf{e}_1\mathbf{e}_2 \quad \text{(squares to -1)}$$
- Phase extraction via: $$\theta = 2\arctan{2(B, \text{scalar})}$$

#### Limitations
- Fixed-step Euler integration (not adaptive like RK45).
- Experimental/research mode. Make sure to validate against classic solver.
- Requires `clifford` package installation.

### Synchronization Transition
```bash
from kuramoto.analysis.spectral import detect_sync_transition

# Detect critical coupling K_c from spectral peak emergence
K_values = np.linspace(0.5, 2.0, 20)
all_psd = [...]  # Array of PSDs for each K value

K_c = detect_sync_transition(freqs, all_psd, K_values)
print(f"Critical coupling K_c:{K_c:.2f}")
```

### Harmonic Cascade Analysis
```bash
from kuramoto.analysis.spectral import harmonic_analysis

# Analyze harmonic content of order parameter oscillations
harm = harmonic_analysis(order_param_timeseries, dt=0.01, max_harmonic=5)

print(f"Fundamental power ratio: {harm['h1_power_ratio']:.2%}")
print(f"H2/H1 ratio: {harm['h2_power_ratio']:.2%}")
print(f"Remaining power: {harm['rest_ratio']:.2%}")
```

---

## 🧬 Lie Symmetry Diagnostics
The Lie symmetry tracking mode monitors:

| **Symmetry** | **Diagnostic** | **Physical Interpretation** |
|:-------------|----------------|-----------------------------|
| $U(1)$ Global Phase | `global_phase_invariant` | Do dynamics respect phase shift? |
| Energy (Noether) | `energy_conserved` | Kinetic + interaction energy over time |
| Synchronization | `synchronization_strength` | Final order parameter $\|r\|$ |

**Output format:** Additional `.json` metadata files accompany `.npz` datasets when `--track-symmetries` is enabled.

---

## 🐉 Visual Identity and Style
The project uses a standard 'house style' for all code visualizations:
- **Gradient Theme:** 8 custom gradients (`gradient_0` to `gradient_7`) for consistent data coloring.
- **Consistent Coloring:** Oscillators are colored by their degree in the network plot, and this coloring is preserved
   across time-series and spectral diagnostics.
- **Seaborn Integration:** Publication-ready plots with high-density markers.
- **House Rules:** Code follows strict emoji-numbered sectioning and NumPy-style documentation 
  (see `templates/HOUSE_RULES.md`).

---

## 📐 Mathematical Model

### Standard Kuramoto Model

$$ \frac{d\theta_i}{dt} = \omega_i + \frac{K}{N} \sum_{j=1}^{N} A_{ij}\sin{(\theta_j - \theta_i)} $$
where $A_{ij}$ is the adjacency matrix and $K$ is the coupling strength.

### Geometric Algebra Formulation (Experimental)

Oscillators represented as rotors in $\operatorname{Cl}(2)$ even subalgebra:
$$R_i(t) = \exp{\bigg(-\frac{B\theta_i(t)}{2}\bigg)} \, , \quad B=\mathbf{e}_1 \wedge \mathbf{e}_2$$

Phase extraction:
$$\theta_i(t) = 2\arctan{\big( \langle R_i \rangle_B , \langle R_i \rangle_0 \big)}$$
where $\langle \cdot \rangle_k$ extracts grade-$k$ component (scalar or bi-vector coefficient).

---

## ⚗️ Simulate via JSON
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
  "seed": 27,
  "solver": "euler",
  "frequency_distribution": {
    "type": "normal",
    "mean": 0.0,
    "std": 1.0
  }
}
```

New solver field values:
- `"euler"` - Standard Euler (default)
- `"rk45"` - SciPy adaptive RK45
- `"rotor"` - Geometric Algebra $\operatorname{Cl}(2)$

---

## ⚠️ Known Limitations

| **Component** | **Limitation** | **Mitigation** |
|:--------------|:--------------|:---------------|
| RotorSolver | Fixed-step Euler, not adaptive | Validate against RK45 for critical runs |
| Stability | Large $K$ or extreme $\omega$ may cause divergence | Use `enforce_nyquist=True` warning mode |
| Dependencies | `clifford` required for GA features | Optional; classic solver works without it |
| Platform | Tested on Windows/macOS/Linux with Python 3.10+ | |

---

## 📄 Lisence
MIT License. See [LICENSE](LICENSE) for details.

## 🔬 Related Work

- **Spectral Analysis Inspiration:** [Satis](https://cerfacs.fr/en/home/)(CFD spectral diagnostics)
- **Geometric Algebra:** Hestenes' Spacetime Algebra (STA), David Hestenes
- **Kuramoto Models:** Original work by Yoshiki Kuramoto (1975)

## 🤝 Contributing
Contributions are welcome! Areas of interest:
- Adaptive stepper for `RotorSolver` (Dormand-Prince RK45)
- Tensor product extensions for multi-system counting
- Higher-dimensional GA ($\operatorname{Cl}(3)$, $\operatorname{Cl}(3,1)$ for relativistic analogs)
- Additional network topologies and chromatic polynomial analysis