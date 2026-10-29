# 🛠️ Kuramoto CLI Usage Guide

This guide provides detailed instructions and examples for using the `kuramoto` command-line interface. The CLI is designed to be the primary way to interact with the suite, offering tools for simulation, quantum execution, benchmarking, and visualization.

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

## 1️⃣ Core Commands

### 🌀 `generate`
The workhorse command. Generates synthetic Kuramoto datasets using various solvers.

**Examples:**
- **Classical RK45:**
  ```bash
  kuramoto generate -n 25 -K 1.5 -t 1000 --dt 0.05 --solver rk45 -o data/rk45.npz
  ```
- **Geometric Algebra Rotor (RKMK4):**
  ```bash
  kuramoto generate -n 50 -K 2.0 -t 500 --dt 0.01 --solver rkmk4 --track-symmetries -o data/rotor_rkmk4.npz
  ```
- **Adaptive Rotor (DOPRI54):**
  ```bash
  kuramoto generate -n 30 -K 1.8 -t 1000 --solver dopri54 --adaptive-rtol 1e-6 --adaptive-atol 1e-8 -o data/rotor_adaptive.npz
  ```
- **Hybrid Quantum SCF:**
  ```bash
  kuramoto generate -n 12 -K 1.5 -t 200 --dt 0.02 --solver quantum --scheme statevector -o data/quantum.npz
  ```

### ⚛️ `quantum`
Dedicated command for running hybrid Quantum Self-Consistent Field (SCF) rotor simulations.

**Examples:**
- **Expectation Scheme:**
  ```bash
  kuramoto quantum -n 10 -K 1.5 -t 200 --dt 0.02 --scheme expectation
  ```
- **Shot-Sampling (Tomography):**
  ```bash
  kuramoto quantum -n 8 -K 2.0 -t 150 --topology ring --scheme shot_sampling --shots 4096 -o data/quantum_ring.npz
  ```

### 🔌 `qasm`
Export Quantum SCF circuits to OpenQASM format.

**Examples:**
- **OpenQASM 2.0:**
  ```bash
  kuramoto qasm -n 8 -K 1.5 --dt 0.05 -o circuits/scf_step.qasm
  ```
- **OpenQASM 3.0 with Measurements:**
  ```bash
  kuramoto qasm -n 16 -K 2.0 --dt 0.02 --version 3.0 --include-measurements -o circuits/scf_qasm3.qasm
  ```

### 🏎️ `benchmark`
Compare performance across different solvers (Classical, GA Rotor, Quantum).

**Example:**
```bash
kuramoto benchmark -n 20 -K 1.5 -t 500 --dt 0.01
```

---

## 2️⃣ Visualization & Diagnostics

These commands help you inspect generated datasets or system properties.

### 🔗 `network`
Visualize the graph topology used for coupling.
```bash
kuramoto network --topology small_world -n 50
```

### 📈 `time`
Plot phase trajectories $\theta_i(t)$ and the global order parameter $r(t)$.
```bash
kuramoto time -i data/rk45.npz
```

### 📊 Spectral Analysis
- `distributions`: Plot frequency and phase initializations.
- `fouriervariability`: Fourier coefficient stability.
- `psdvariability`: Power Spectral Density analysis.

---

## 3️⃣ Beginner Tools

### 🔰 `datasetforbeginners`
Quickly generate a standard demo dataset to start exploring.
```bash
kuramoto datasetforbeginners -o data/demo.npz
```

---

## 📂 Where to find Demos?
All interactive demonstrations are now located in:
`examples/ai_generated_notebooks/`

Check out the notebooks there for deep-dives into Geometric Algebra, Quantum integration, and solver validation!
