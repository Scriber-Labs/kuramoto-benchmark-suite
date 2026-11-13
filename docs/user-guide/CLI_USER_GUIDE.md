# 📟 Kuramoto Benchmark Suite — CLI User Guide

Welcome to the definitive user guide for the `kuramoto` Command Line Interface (CLI). This guide covers the full command suite, simulation workflows, quantum circuit generation, Geometric Algebra (GA) rotor mechanics, spectral analysis tools, and telemetry export.

---

## 0️⃣ Overview & Design Philosophy

The `kuramoto` CLI is engineered as a unified research terminal providing high-performance simulation dispatching, real-time diagnostic telemetry, and publication-ready visualization generation.

### Key Capabilities
- **Multi-Paradigm Solvers**: Classical adaptive ODEs (`rk45`), Geometric Algebra Clifford rotors on $\operatorname{Spin}(n)$ (`euler`, `midpoint`, `rkmk4`, `dopri54`, `adaptive`), and hybrid Quantum Self-Consistent Field (SCF) solvers (`statevector`, `expectation`, `shot_sampling`).
- **Telemetry & Manifold Invariants**: Tracking Hamiltonian energy drift, phase-space volume contraction, and global $U(1)$ / $\operatorname{SO}(2)$ Lie group gauge symmetry.
- **Spectral Analytics**: Instant Fourier amplitude variability, Fourier convergence, and Power Spectral Density (PSD) analysis.
- **Sub-Nyquist & Mesoscale Dynamics**: ZBW ($\phi$-shield) golden-ratio frequency grids, coprime adjacency lattices, and external macroscopic LED driving fields.
- **Dash Ecosystem Interoperability**: Enriched JSON telemetry streaming (`dash-export`) for the `kuramoto-dash-app`.
- **Scriber Core Semantic Palette**: ANSI 256 / Truecolor output with high-contrast attention anchors (`cli_info`, `cli_network`, `cli_quantum`, `cli_rotor`, `cli_success`, `cli_warning`, `cli_error`).

---

## 1️⃣ Quickstart & Environment Setup

Run commands directly with `uv run kuramoto` or by activating your virtual environment:

```bash
# Recommended execution with uv
uv run kuramoto --help

# Or within an activated virtual environment
source .venv/bin/activate
kuramoto --help
```

---

## 2️⃣ Complete Command Reference

The CLI provides 14 primary subcommands organized into distinct functional categories:

```
Commands:
  datasetforbeginners  Generate a quick starter dataset for beginners.
  generate             Generate a dataset from a JSON configuration file.
  quantum              Run a dedicated Quantum SCF simulation.
  qasm                 Generate and export OpenQASM 2.0 quantum circuits.
  benchmark            Benchmark performance and accuracy across solvers.
  time                 Plot phase time series and order parameter r(t).
  network              Plot network graph topology and connectivity.
  distributions        Plot natural frequency and phase distributions.
  fouriervariability   Plot Fourier coefficient variability across oscillators.
  fourierconvergence   Plot Fourier coefficient convergence over time.
  psdvariability       Plot Power Spectral Density (PSD) variability.
  psdconvergence       Plot PSD convergence across time windows.
  dash-export          Run simulation and export enriched JSON for Dash app.
  zbw                  Simulate ZBW mesoscale golden-ratio ensemble.
```

---

### 2.1 Dataset Generation & Simulation

#### 🔰 `datasetforbeginners`
Generate a ready-to-use synthetic Kuramoto dataset with small-world topology ($N=50$, $K=2.0$, $T=1000$, $\Delta t=0.05$).

```bash
kuramoto datasetforbeginners -o data/starter_demo.npz
```
- **Options**:
  - `-o, --output PATH`: Target `.npz` file path (default: `data/examples/small_demo.npz`).

---

#### 🌀 `generate`
The primary production command for batch simulation from a JSON configuration file, supporting classical, geometric, and quantum solvers with symmetry tracking and adaptive tolerances.

```bash
# 1. Classical adaptive RK45
kuramoto generate -c data/benchmark/config.json -s rk45 -o data/classical_rk45.npz

# 2. 4th-Order Lie-Group RKMK4 with Lie Symmetry Tracking
kuramoto generate -c data/benchmark/config.json -s rkmk4 --track-symmetries -o data/rotor_rkmk4.npz

# 3. 5th-Order Embedded Adaptive DOPRI54 with Step Controller
kuramoto generate -c data/benchmark/config.json -s dopri54 --adaptive-rtol 1e-6 --adaptive-atol 1e-8 -o data/rotor_dopri54.npz

# 4. Quantum SCF Simulation with QASM Circuit Export
kuramoto generate -c data/benchmark/config.json -s quantum --scheme expectation -q circuits/step_circuit.qasm -o data/quantum_scf.npz
```

- **Options**:
  - `-c, --config PATH` *(Required)*: Path to simulation JSON configuration file.
  - `-s, --solver [euler|rk45|rotor|rkmk4|dopri54|quantum|...]`: Solver choice (default: `euler`).
  - `-o, --output PATH`: Output dataset path (`.npz`).
  - `--scheme [statevector|expectation|shot_sampling]`: Quantum execution scheme.
  - `--shots INTEGER`: Shot count for quantum projective measurement (default: `1024`).
  - `--dt-internal FLOAT`: Internal sub-stepping time increment.
  - `--enforce-nyquist / --no-nyquist`: Toggle Nyquist temporal resolution guard.
  - `--adaptive-rtol FLOAT`: Relative tolerance for adaptive Lie-group steppers.
  - `--adaptive-atol FLOAT`: Absolute tolerance for adaptive Lie-group steppers.
  - `-q, --qasm-out PATH`: Optional path to export OpenQASM 2.0 quantum circuit.
  - `--track-symmetries`: Enable $U(1)$ gauge invariance and Noether energy tracking.

---

#### ⚛️ `quantum`
Run an end-to-end Quantum Self-Consistent Field (SCF) simulation on the Bloch sphere with real-time CLI telemetry and optional trajectory plotting.

```bash
# Expectation value scheme with instant visual plot
kuramoto quantum -n 12 -k 1.8 -t 200 --dt 0.05 --scheme expectation --plot

# Stochastic shot-sampling tomography with 4096 shots
kuramoto quantum -n 8 -k 2.0 -t 150 --scheme shot_sampling --shots 4096 -o data/quantum_shots.npz
```

- **Options**:
  - `-n, --oscillators INTEGER`: Number of qubits / oscillators (min: 2, default: `10`).
  - `-k, --coupling FLOAT`: Coupling strength $K$ (default: `1.5`).
  - `-t, --timesteps INTEGER`: Integration timesteps (default: `100`).
  - `--dt FLOAT`: Time step increment (default: `0.05`).
  - `--scheme [statevector|expectation|shot_sampling]`: Quantum execution mode.
  - `--shots INTEGER`: Tomographic shot budget for `shot_sampling`.
  - `--seed INTEGER`: Random seed for reproducible frequencies.
  - `-o, --output PATH`: Output path for `.npz` dataset.
  - `--plot / --no-plot`: Automatically generate and display trajectory plot.

---

#### 🔌 `qasm`
Generate and export OpenQASM 2.0 / 3.0 quantum circuit definitions from a dataset snapshot or synthetic parameters.

```bash
# Generate QASM from an existing simulation dataset snapshot
kuramoto qasm -d data/rotor_rkmk4.npz -o circuits/scf_update.qasm

# Generate QASM from raw parameters
kuramoto qasm -n 16 -k 2.0 --dt 0.02 -o circuits/scf_step_16q.qasm
```

- **Options**:
  - `-d, --dataset PATH`: Source dataset to extract final phase positions.
  - `-n, --oscillators INTEGER`: Number of qubits if generating synthetically.
  - `-k, --coupling FLOAT`: Coupling coefficient.
  - `--dt FLOAT`: Integration time step.
  - `-o, --output PATH`: Output `.qasm` file path.

---

#### 🌌 `zbw`
Execute a ZBW (Zitterbewegung) mesoscale simulation incorporating the $\phi$-shield golden-ratio frequency grid, sparse coprime adjacency lattice, and external macroscopic LED driving field.

```bash
# Standard ZBW ensemble with external LED driving and trajectory plot
kuramoto zbw -n 20 -t 500 --dt 0.01 -k 1.5 --base-freq 40.0 --external-drive --drive-strength 0.8 --drive-freq 40.0 --plot -o data/zbw_cff.npz
```

- **Options**:
  - `-n, --oscillators INTEGER`: Oscillator count (default: `20`).
  - `-t, --timesteps INTEGER`: Timestep count (default: `500`).
  - `--dt FLOAT`: Integration time step (default: `0.01`).
  - `-k, --coupling FLOAT`: Coupling constant (default: `1.5`).
  - `-f, --base-freq FLOAT`: Fundamental frequency in Hz (default: `40.0`).
  - `--external-drive / --no-external-drive`: Toggle macroscopic driving field.
  - `--drive-strength FLOAT`: External field coupling $K_{\text{ext}}$.
  - `--drive-freq FLOAT`: Drive frequency in Hz.
  - `-o, --output PATH`: Output `.npz` file path.
  - `--plot / --no-plot`: Toggle trajectory and order parameter visualization.

---

### 2.2 Telemetry & Dash Ecosystem Bridge

#### 📊 `dash-export`
Execute a simulation and produce enriched JSON telemetry tailored for direct ingestion by the `kuramoto-dash-app`. Computes mean-field phase $\psi(t)$ and sliding-window frequency locking fraction.

```bash
kuramoto dash-export -n 50 -k 1.8 -t 300 --topology small_world --solver rk45 --window 15 --threshold 0.05 -o data/dash_telemetry.json
```

- **Options**:
  - `-n, --oscillators INTEGER`: Node count (default: `50`).
  - `-k, --coupling FLOAT`: Coupling strength $K$ (default: `1.5`).
  - `-t, --timesteps INTEGER`: Timestep count (default: `200`).
  - `--dt FLOAT`: Time step increment (default: `0.05`).
  - `--topology [ring|small_world|tree_of_life|bipartite|erdos_renyi|complete]`: Graph topology.
  - `--noise FLOAT`: Gaussian phase noise standard deviation $\sigma$.
  - `--solver [rk45|euler|rotor|rkmk4|dopri54|quantum]`: Solver method.
  - `--window INTEGER`: Sliding window size for frequency locking detection (default: `10`).
  - `--threshold FLOAT`: Locking detection frequency tolerance (default: `0.1`).
  - `-o, --output PATH`: Target `.json` file path.

---

### 2.3 Diagnostics, Benchmarking & Visual Analytics

#### 🏎️ `benchmark`
Run a comparative performance, wall-clock speedup, and numerical accuracy benchmark comparing classical RK45 against Geometric Algebra rotor steppers and Quantum SCF solvers.

```bash
kuramoto benchmark -n 50 -k 1.5 -t 500 --dt 0.01 --seed 42
```

- **Options**:
  - `-n, --oscillators INTEGER`: System size (default: `20`).
  - `-k, --coupling FLOAT`: Coupling strength (default: `1.5`).
  - `-t, --timesteps INTEGER`: Step count (default: `500`).
  - `--dt FLOAT`: Time step increment (default: `0.01`).
  - `--seed INTEGER`: Random seed.

---

#### 📈 `time`
Plot individual phase trajectories $\theta_i(t)$ alongside the macroscopic order parameter $r(t)$.

```bash
kuramoto time data/rotor_rkmk4.npz -o plots/time_series.png --title "RKMK4 Phase Dynamics"
```

- **Options**:
  - `DATASET_PATH` *(Argument)*: Path to input `.npz` dataset.
  - `-o, --output PATH`: Target image path (default: `plots/time.png`).
  - `--title TEXT`: Custom plot title.

---

#### 🌐 `network`
Visualize network graph topology with node color-coding matching the Scriber Core palette and graph layout metrics.

```bash
kuramoto network data/rotor_rkmk4.npz -o plots/network_topology.png
```

- **Options**:
  - `DATASET_PATH` *(Argument)*: Input `.npz` dataset.
  - `-o, --output PATH`: Target image path (default: `plots/network.png`).
  - `--title TEXT`: Plot title.

---

#### 📊 `distributions`
Plot initial phase distributions on the circle and natural frequency histograms $\omega_i \sim g(\omega)$.

```bash
kuramoto distributions data/classical_rk45.npz -o plots/initial_distributions.png
```

---

#### 🔍 Spectral Analysis Suite
- **`fouriervariability DATASET_PATH --freq FLOAT`**: Measure Fourier coefficient variability across oscillators.
- **`fourierconvergence DATASET_PATH --freq FLOAT`**: Track Fourier mode convergence as a function of integration time.
- **`psdvariability DATASET_PATH --freq FLOAT`**: Compute Power Spectral Density (PSD) variance across nodes.
- **`psdconvergence DATASET_PATH --freq FLOAT`**: Analyze PSD energy convergence across windowed segments.

```bash
# Evaluate PSD variability at fundamental frequency 1.0 rad/s
kuramoto psdvariability data/rotor_rkmk4.npz --freq 1.0 -o plots/psd_var.png

# Evaluate Fourier mode convergence
kuramoto fourierconvergence data/rotor_rkmk4.npz --freq 1.0 -o plots/fourier_conv.png
```

---

## 3️⃣ Production Research Workflows

### Workflow A: Geometric Algebra Invariant Validation
1. Create or edit a simulation config in `data/benchmark/config.json`.
2. Run RKMK4 with Lie symmetry tracking:
   ```bash
   kuramoto generate -c data/benchmark/config.json -s rkmk4 --track-symmetries -o data/geom_run.npz
   ```
3. Generate time-series and network topology plots:
   ```bash
   kuramoto time data/geom_run.npz -o plots/geom_time.png
   kuramoto network data/geom_run.npz -o plots/geom_net.png
   ```

### Workflow B: Telemetry Streaming to `kuramoto-dash-app`
1. Generate enriched telemetry:
   ```bash
   kuramoto dash-export -n 100 -k 2.2 -t 500 --topology small_world -o ../kuramoto-dash-app/data/telemetry.json
   ```
2. Open the Dash app dashboard to visualize mean-field phase $\psi(t)$ and dynamic locking fraction in real-time.

### Workflow C: Quantum SCF Circuit Generation & Verification
1. Run the quantum expectation solver:
   ```bash
   kuramoto quantum -n 8 -k 1.5 -t 100 --scheme expectation -o data/q_run.npz --plot
   ```
2. Export the final-state quantum circuit to OpenQASM:
   ```bash
   kuramoto qasm -d data/q_run.npz -o circuits/scf_final.qasm
   ```

---

## 4️⃣ Exit Codes & Error Handling

| Exit Status / Code | Cause | Resolution |
| :--- | :--- | :--- |
| `0` (Success) | Clean simulation and output serialization. | Output available at specified path. |
| `Missing Config` | `--config` not supplied to `generate`. | Provide path via `-c data/config.json`. |
| `Nyquist Warning` | $\Delta t > 1 / (2 \omega_{\max})$. | Enable sub-stepping via `--dt-internal` or use `--no-nyquist`. |
| `Topology Error` | Non-symmetric or disconnected graph. | Validate adjacency matrix in config. |

---
*Maintained by Scriber Labs & Eigenscribe.*
