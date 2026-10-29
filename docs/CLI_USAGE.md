# 🛠️ Scriber Labs: Kuramoto CLI Usage Guide

This guide provides detailed instructions and examples for using the `kuramoto` command-line interface. The CLI is the primary gateway to the **Scriber Labs** simulation engine, offering tools for mesoscale dynamics, quantum execution, and geometric analysis.

---

## 0️⃣ General Command Structure

All commands follow the pattern:
```bash
kuramoto <command> [OPTIONS]
```
Use `--help` with any command to see all available flags:
```bash
kuramoto generate --help
```

---

## 1️⃣ Simulation & Data Generation

### 🌀 `generate`
The core command for synthetic Kuramoto datasets. It supports classical, geometric, and quantum-hybrid solvers.

**Examples:**
- **Mesoscale ZBW Simulation (Classical RK45):**
  ```bash
  kuramoto generate -n 100 -K 0.8 --solver rk45 -o data/zbw_meso.npz
  ```
- **Geometric Algebra Rotor (RKMK4):**
  ```bash
  kuramoto generate -n 50 -K 2.0 --solver rkmk4 --track-symmetries -o data/rotor_rkmk4.npz
  ```
- **Adaptive Rotor (DOPRI54):**
  ```bash
  kuramoto generate -n 30 -K 1.8 --solver dopri54 --adaptive-rtol 1e-6 -o data/rotor_adaptive.npz
  ```

### ⚛️ `quantum`
Dedicated command for running hybrid Quantum Self-Consistent Field (SCF) rotor simulations.

**Examples:**
- **Expectation Scheme:**
  ```bash
  kuramoto quantum -n 10 -K 1.5 -t 200 --scheme expectation
  ```
- **Shot-Sampling (Tomography):**
  ```bash
  kuramoto quantum -n 8 -K 2.0 -t 150 --scheme shot_sampling --shots 4096 -o data/quantum_shots.npz
  ```

---

## 2️⃣ Visualization & Diagnostics

### 🔗 `network`
Visualize the graph topology used for coupling (e.g., ring, small-world, erdos-renyi).
```bash
kuramoto network --topology small_world -n 50
```

### 📈 `time`
Plot phase trajectories $\theta_i(t)$ and the global order parameter $r(t)$.
```bash
kuramoto time -i data/zbw_meso.npz
```

### 📊 Spectral Analysis
- `distributions`: Plot frequency and phase initializations (e.g., Uniform, Lorentzian, or **phi-Shield**).
- `fouriervariability`: Fourier coefficient stability across the ensemble.
- `psdvariability`: Power Spectral Density analysis for frequency-domain diagnostics.

---

## 3️⃣ Advanced Research Tools

### 🏎️ `benchmark`
Compare performance and conservation accuracy across different solvers.
```bash
kuramoto benchmark -n 20 -K 1.5 -t 500 --dt 0.01
```

### 🔌 `qasm`
Export Quantum SCF circuits to OpenQASM format for execution on real hardware or external simulators.
```bash
kuramoto qasm -n 8 -K 1.5 --version 3.0 --include-measurements -o circuits/scf_step.qasm
```

---

## 📂 AI-Generated Demos
For interactive research and new mesoscale models (like the **ZBW Coprime Adjacency** generator), please visit:
👉 `examples/ai_generated_notebooks/`

We store all evolving proof-of-concepts there to maintain a clean production CLI while allowing rapid research iteration.
