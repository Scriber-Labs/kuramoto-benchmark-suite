# 🛠️ Scriber Labs: Kuramoto CLI Usage Guide

This guide provides detailed instructions and examples for using the `kuramoto` command-line interface. The CLI is the primary gateway to the **Scriber Labs** simulation engine, offering tools for mesoscale dynamics, quantum execution, and geometric analysis.

---

## 0️⃣ General Command Structure

All commands follow the pattern:
```bash
kuramoto <command> [OPTIONS]
```
Run the command from an activated project environment, or use `uv run kuramoto`
when using `uv` without activating the environment.
Use `--help` with any command to see all available flags:
```bash
kuramoto generate --help
```

---

## 1️⃣ Simulation & Data Generation

### 🌀 `generate`
The core command for synthetic Kuramoto datasets. It supports classical, geometric, and quantum-hybrid solvers.

**Examples:**
- **Mesoscale Simulation (Classical RK45):**
  ```bash
  kuramoto generate --config data/benchmark/config.json --solver rk45 -o data/zbw_meso.npz
  ```
- **Geometric Algebra Rotor (RKMK4):**
  ```bash
  kuramoto generate --config data/benchmark/config.json --solver rkmk4 --track-symmetries -o data/rotor_rkmk4.npz
  ```
- `generate` reads oscillator count, coupling, topology, and timestep settings from
  the JSON config. Solver settings can be overridden with CLI options.
- **Adaptive Rotor (DOPRI54):**
  ```bash
  kuramoto generate --config data/benchmark/config.json --solver dopri54 --adaptive-rtol 1e-6 -o data/rotor_adaptive.npz
  ```

### ⚛️ `quantum`
Dedicated command for running hybrid Quantum Self-Consistent Field (SCF) rotor simulations.

**Examples:**
- **Expectation Scheme:**
  ```bash
  kuramoto quantum -n 10 -k 1.5 -t 200 --scheme expectation
  ```
- **Shot-Sampling (Tomography):**
  ```bash
  kuramoto quantum -n 8 -k 2.0 -t 150 --scheme shot_sampling --shots 4096 -o data/quantum_shots.npz
  ```

---

## 2️⃣ Visualization & Diagnostics

### 🔗 `network`
Visualize the graph topology from a generated dataset.
```bash
kuramoto network data/mesoscale.npz
```

### 📈 `time`
Plot phase trajectories $\theta_i(t)$ and the global order parameter $r(t)$.
```bash
kuramoto time data/zbw_meso.npz
```

### 📊 Spectral Analysis
- `distributions DATASET_PATH`: Plot frequency and phase initializations from a dataset.
- `fouriervariability DATASET_PATH --freq FREQUENCY`: Fourier coefficient stability across the ensemble.
- `psdvariability DATASET_PATH --freq FREQUENCY`: Power Spectral Density analysis for frequency-domain diagnostics.

---

## 3️⃣ Advanced Research Tools

### 🏎️ `benchmark`
Compare performance and conservation accuracy across different solvers.
```bash
kuramoto benchmark -n 20 -k 1.5 -t 500 --dt 0.01
```

### 🔌 `qasm`
Export Quantum SCF circuits to OpenQASM 2.0 format for execution on real hardware or external simulators.
```bash
kuramoto qasm --dataset data/mesoscale.npz -o circuits/scf_step.qasm
```

---

## 📂 AI-Generated Demos
For interactive research and new mesoscale models (like the **ZBW Coprime Adjacency** generator), please visit:
👉 `notebooks/ai_generated/`

We store all evolving proof-of-concepts there to maintain a clean production CLI while allowing rapid research iteration.
